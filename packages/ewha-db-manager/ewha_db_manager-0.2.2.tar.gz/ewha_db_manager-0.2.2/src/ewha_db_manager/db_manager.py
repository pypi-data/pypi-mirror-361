# ewha_trajdb_manager.py

"""
Import trajectories to process CCTV DataFrames

Code writer : Jiyoon Lee
E-mail : jiyoon821@ewha.ac.kr

Last update : 2025. 04. 29.

"""

import psycopg2
import pandas as pd
import geopandas as gpd
import movingpandas as mpd
import sys
import logging
from tqdm import tqdm
from typing import Dict
from psycopg2.extras import execute_values

logging.basicConfig(level = logging.INFO, format = "%(asctime)s - %(levelname)s - %(message)s")


class DBManager:
    """
    A manager for connecting to a PostgreSQL database, importing data,
    processing trajectory attributes, and grouping data by CCTV ID.
    """

    def __init__(self, host: str, port: int, dbname: str, user: str, password: str, schema = None):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password

        def find_view_schema(cursor, view_name='cctv_fov_road'):
            query = f"""
            SELECT table_schema, table_name
            FROM information_schema.views
            WHERE table_name = %s;
            """
            cursor.execute(query, (view_name,))
            results = cursor.fetchall()
            return results

        try:
            self.conn = psycopg2.connect(
                host = self.host,
                port = self.port,
                dbname = self.dbname,
                user = self.user,
                password = self.password
            )
            self.cur = self.conn.cursor()
            logging.info("Database connection established successfully.")

            schema_info = []
            try:
                view_locations = find_view_schema(self.cur, schema)
                if view_locations:
                    for schema, table in view_locations:
                        logging.info(f"View '{table}' found in schema: {schema}")
                        schema_info.append(schema)
                else:
                    logging.warning("View 'cctv_fov_road' not found in any schema.")
            except Exception as e:
                logging.error(f"Error while searching for view: {e}")
            schema_info = repr(schema_info[0])
            if schema:
                schema_query = f"SELECT table_name FROM information_schema.tables WHERE table_schema = {schema_info};"
                self.cur.execute(schema_query)
                rows = self.cur.fetchall()
                logging.info(f"Tables in {schema_info} schema: {rows}")
            else:
                schema_query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'collect';"
                self.cur.execute(schema_query)
                rows = self.cur.fetchall()
                logging.info(f"Tables in 'collect' schema: {rows}")

        except Exception as e:
            logging.error(f"Failed to connect to the database: {e}")
            raise

    def close(self):
        """Closes the database connection safely."""
        if hasattr(self, "cur") and self.cur:
            self.cur.close()
        if hasattr(self, "conn") and self.conn:
            self.conn.close()
        logging.info("Database connection closed.")

    def upload_dataframe_to_postgres(self, df, table_name, schema, mode='insert', conflict_columns=None, update_columns=None):
        columns = ', '.join(df.columns)
        values = [tuple(x) for x in df.to_numpy()]
        placeholders = '%s'

        base_query = f"INSERT INTO {schema}.{table_name} ({columns}) VALUES {placeholders}"

        # Mode handling
        if mode == 'replace':
            if not conflict_columns or not update_columns:
                raise ValueError("For 'replace' mode, conflict_columns and update_columns must be provided.")
            conflict_cols = ', '.join(conflict_columns)
            update_set = ', '.join([f"{col} = EXCLUDED.{col}" for col in update_columns])
            base_query += f" ON CONFLICT ({conflict_cols}) DO UPDATE SET {update_set}"
        elif mode == 'insert' or mode == 'append':
            pass  # 기본 insert 동작
        else:
            raise ValueError("Mode must be one of ['insert', 'append', 'replace']")

        try:
            with self.conn.cursor() as cur:
                execute_values(cur, base_query, values)
                self.conn.commit()
                print(f"✅ {mode.upper()} success: {len(df)} rows into {schema}.{table_name}")
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Failed to {mode} data: {e}")

    def clear_table(self, schema, table_name):
        try:
            with self.conn.cursor() as cur:
                cur.execute(f"DELETE FROM {schema}.{table_name};")
                self.conn.commit()
                print(f"✅ All rows deleted from {schema}.{table_name}")
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Failed to delete rows: {e}")



    def import_data(self, table: str, schema = None) -> pd.DataFrame:
        """
        Imports all data from a given table using a server-side cursor.

        Args:
            table (str): Table name to import from.

        Returns:
            pd.DataFrame: Imported table data.
        """
        if schema:
            schema = schema
        else:
            schema = 'collect'

        try:
            count_query = f"SELECT COUNT(*) FROM {schema}.{table};"
            self.cur.execute(count_query)
            total_rows = self.cur.fetchone()[0]
            logging.info(f"Fetching {total_rows} rows from {table}.")

            named_cursor = self.conn.cursor(name = f"server_cursor_{table}")
            named_cursor.itersize = 1000
            table_query = f"SELECT * FROM {schema}.{table};"
            named_cursor.execute(table_query)

            first_row = next(named_cursor)
            col_names = [desc[0] for desc in named_cursor.description]
            rows = [first_row]

            for _, row in enumerate(tqdm(named_cursor, total = total_rows,
                                         desc = "Fetching rows",
                                         ncols = 100, file = sys.stdout,
                                         bar_format = "{l_bar}{bar} | {n_fmt}/{total_fmt} [{elapsed} elapsed]")):
                rows.append(row)
            logging.info(f"Actual number of imported rows is {total_rows}, not {total_rows - 1}.")

            df = pd.DataFrame(rows, columns=col_names)
            named_cursor.close()
            return df


        except Exception as e:
            logging.error(f"Error during data import: {e}")
            raise

    def add_attribute(self, df: pd.DataFrame) -> gpd.GeoDataFrame:
        """
        Adds trajectory attributes (acceleration, speed, etc.) to the data.

        Args:
            df (pd.DataFrame): DataFrame containing at least lon, lat, and dtct_dt columns.

        Returns:
            gpd.GeoDataFrame: GeoDataFrame with trajectory attributes.
        """
        gdf = gpd.GeoDataFrame(df, geometry = gpd.points_from_xy(df["lon"], df["lat"]))
        gdf["dtct_dt"] = pd.to_datetime(gdf["dtct_dt"]).apply(lambda dt: dt.replace(microsecond=0))
        gdf["dtct_dt"] = gdf["dtct_dt"].dt.tz_localize(None)
        gdf = gdf.set_index(pd.DatetimeIndex(gdf["dtct_dt"]))
        gdf = gdf.set_crs("epsg:4326")

        traj_collection = mpd.TrajectoryCollection(gdf, "mf_id")
        traj_collection.add_acceleration()
        traj_collection.add_angular_difference()
        traj_collection.add_direction()
        traj_collection.add_speed()
        traj_collection.add_distance()
        traj_collection.add_traj_id(overwrite=False)

        return traj_collection.to_point_gdf()

    def dataframe_groups(self, table_name: str) -> Dict[str, gpd.GeoDataFrame]:
        """
        Imports data and groups it by CCTV ID after processing trajectory attributes.

        Args:
            table_name (str): Table name to import and process.

        Returns:
            Dict[str, gpd.GeoDataFrame]: Dictionary mapping CCTV IDs to processed GeoDataFrames.
        """        
        df = self.import_data(table_name)
        self.close()

        df_group = {}
        cctv_ids = df["snr_id"].unique()

        logging.info(f"Processing {len(cctv_ids)} CCTV IDs.")

        for cctv_id in tqdm(cctv_ids, total = len(cctv_ids),
                            desc = "CCTV Preprocessing",
                            ncols = 100,
                            bar_format = "{l_bar}{bar} | {n_fmt}/{total_fmt} [{elapsed} elapsed]"):
            df_by_cctv = self.add_attribute(df.loc[df["snr_id"] == cctv_id])
            df_group[cctv_id] = df_by_cctv

        logging.info("Data processing completed. Returning CCTV data groups.")
        logging.info("Output data format : dictionary. e.g. {cctv id : dataframe}")
        
        return df_group
