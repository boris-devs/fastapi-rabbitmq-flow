from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	POSTGRES_USER: str = "postgres"
	POSTGRES_PASSWORD: str = "postgres"
	POSTGRES_DB: str = "task_scheduler"
	POSTGRES_PORT: int = 5432
	POSTGRES_HOST: str = "localhost"

	ACCESS_SECRET_KEY: str = "access"
	REFRESH_SECRET_KEY: str = "refresh"
	ALGORITHM: str = "HS256"
	ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
	REFRESH_TOKEN_EXPIRE_DAYS: int = 60 * 24 * 7

	RABBITMQ_AMQP_URL: str = "amqp://guest:guest@localhost:5672/"

	GMAIL_EMAIL: str = ""
	GMAIL_PASSWORD: str = ""
	EMAIL_HOSTNAME: str = "smtp.gmail.com"
	EMAIL_PORT: int = 465

	model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

	@property
	def postgres_database_url(self) -> str:
		return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()
