class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
    os.makedirs(INSTANCE_DIR, exist_ok=True)

    DB_PATH = os.path.join(INSTANCE_DIR, "app.db")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + DB_PATH.replace("\\", "/")
    )

    # ---- i18n ----
    BABEL_DEFAULT_LOCALE = "en"
    BABEL_SUPPORTED_LOCALES = ["en", "es", "fr"]
    BABEL_TRANSLATION_DIRECTORIES = "translations"

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
