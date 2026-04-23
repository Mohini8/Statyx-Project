import express, { type Express } from "express";
import { ServerResponse } from "http";
import cors from "cors";
import pinoHttp from "pino-http";
import session from "express-session";
import { createProxyMiddleware } from "http-proxy-middleware";
import router from "./routes";
import { logger } from "./lib/logger";

const app: Express = express();

app.use(
  pinoHttp({
    logger,
    serializers: {
      req(req) {
        return {
          id: req.id,
          method: req.method,
          url: req.url?.split("?")[0],
        };
      },
      res(res) {
        return {
          statusCode: res.statusCode,
        };
      },
    },
  }),
);
app.use(cors({ origin: true, credentials: true }));

app.use(
  session({
    secret: process.env.SESSION_SECRET ?? "statyx-ai-secret",
    resave: false,
    saveUninitialized: false,
    cookie: {
      secure: process.env.NODE_ENV === "production",
      httpOnly: true,
      maxAge: 7 * 24 * 60 * 60 * 1000,
      sameSite: process.env.NODE_ENV === "production" ? "none" : "lax",
    },
  }),
);

// Proxy /streamlit to Streamlit server
// Express strips the /streamlit prefix via app.use(), so we add it back via pathRewrite
// to match Streamlit's baseUrlPath = "streamlit"
const streamlitPort = process.env.STREAMLIT_PORT ?? "8501";
app.use(
  "/streamlit",
  createProxyMiddleware({
    target: `http://localhost:${streamlitPort}`,
    changeOrigin: true,
    ws: true,
    pathRewrite: (path) => `/streamlit${path}`,
    on: {
      error: (err, req, res) => {
        logger.warn({ err }, "Streamlit proxy error");
        if (res instanceof ServerResponse && !res.headersSent) {
          res.writeHead(503, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: "Analytics engine unavailable" }));
        }
      },
    },
  }),
);

const pythonApiPort = process.env.PYTHON_API_PORT ?? "8502";
app.use(
  "/api/python",
  createProxyMiddleware({
    target: `http://localhost:${pythonApiPort}/api/python`,
    changeOrigin: true,
    secure: false,
    on: {
      error: (err, req, res) => {
        logger.warn({ err }, "Python backend proxy error");
        if (res instanceof ServerResponse && !res.headersSent) {
          res.writeHead(503, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: "Python backend unavailable" }));
        }
      },
    },
  }),
);

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use("/api", router);

export default app;
