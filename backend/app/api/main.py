from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .database import database
from .graphql_schema import schema
from .graphql.context import Context
import logging
import traceback
from graphql import graphql
from openai import AsyncOpenAI
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database...")
    try:
        database.init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise e


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# GraphQL endpoint
@app.post("/graphql")
async def graphql_endpoint(request: Request):
    try:
        data = await request.json()
        operation_name = data.get("operationName", "")
        logger.info(f"GraphQL Operation: {operation_name}")

        context = Context()
        context.db = next(database.get_db())

        try:
            result = await graphql(
                schema.graphql_schema,
                data.get("query"),
                context_value=context,
                operation_name=operation_name,
                variable_values=data.get("variables"),
            )

            if result.errors:
                logger.error(f"GraphQL Errors: {result.errors}")
                return {
                    "data": result.data,
                    "errors": [str(error) for error in result.errors],
                }

            return {"data": result.data}

        except Exception as e:
            logger.error(f"Execution error: {e}")
            logger.error(traceback.format_exc())
            return {"errors": [str(e)]}

    except Exception as e:
        logger.error(f"Request error: {e}")
        logger.error(traceback.format_exc())
        return {"errors": [str(e)]}
    finally:
        if hasattr(context, "db"):
            context.db.close()


# GraphiQL interface
@app.get("/graphql")
async def graphql_playground():
    from fastapi.responses import HTMLResponse

    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>GraphiQL</title>
        <link href="https://unpkg.com/graphiql/graphiql.min.css" rel="stylesheet" />
    </head>
    <body style="margin: 0;">
        <div id="graphiql" style="height: 100vh;"></div>
        <script crossorigin src="https://unpkg.com/react/umd/react.production.min.js"></script>
        <script crossorigin src="https://unpkg.com/react-dom/umd/react-dom.production.min.js"></script>
        <script crossorigin src="https://unpkg.com/graphiql/graphiql.min.js"></script>
        <script>
            const fetcher = GraphiQL.createFetcher({
                url: '/graphql',
            });
            ReactDOM.render(
                React.createElement(GraphiQL, { fetcher: fetcher }),
                document.getElementById('graphiql'),
            );
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/")
async def read_root():
    return {"message": "Patent Checker API is running"}


# Add this new endpoint
@app.get("/test-openai")
async def test_openai():
    """Test endpoint to verify OpenAI API key"""
    try:
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Try a simple completion with gpt-3.5-turbo
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a test responder."},
                {"role": "user", "content": "Say 'OpenAI connection successful!'"},
            ],
            max_tokens=20,
        )

        return {
            "status": "success",
            "message": "OpenAI API connection successful",
            "response": response.choices[0].message.content,
        }

    except Exception as e:
        logger.error(f"OpenAI API test failed: {str(e)}")
        return {"status": "error", "message": f"OpenAI API test failed: {str(e)}"}
