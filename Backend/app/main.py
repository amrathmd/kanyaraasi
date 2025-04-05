# fastapi
from fastapi import FastAPI
from app.core.database import engine
from app.core.modules import init_routers, make_middleware
import app.models.user
import app.models.account
import app.models.document
import app.models.document_info



def create_app() -> FastAPI:
    app.models.user.Base.metadata.create_all(bind=engine)
    app.models.document.Base.metadata.create_all(bind=engine)
    app.models.document_info.Base.metadata.create_all(bind=engine)
    app.models.account.Base.metadata.create_all(bind=engine)
    app.models.document_info.Base.metadata.create_all(bind=engine)
    app_ = FastAPI(
        title="kanyaraasi",
        description="Backend project to automate wellness claims",
        version="1.0.0",
        # dependencies=[Depends(Logging)],
        middleware=make_middleware(),
    )
    init_routers(app_=app_)
    return app_


app = create_app()
