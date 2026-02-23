from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )

    db_type: Literal['sqlite', 'mysql'] = Field(default='sqlite', alias='DB_TYPE')
    
    sqlite_path: Path = Field(default=Path('db/main_database.db'), alias='SQLITE_PATH')
    
    mysql_host: str = Field(default='localhost', alias='MYSQL_HOST')
    mysql_port: int = Field(default=3306, alias='MYSQL_PORT')
    mysql_user: str = Field(default='root', alias='MYSQL_USER')
    mysql_password: str = Field(default='', alias='MYSQL_PASSWORD')
    mysql_database: str = Field(default='chemical_calc', alias='MYSQL_DATABASE')
    
    app_name: str = Field(default='Chemical Calculations', alias='APP_NAME')
    debug: bool = Field(default=False, alias='DEBUG')


settings = Settings()