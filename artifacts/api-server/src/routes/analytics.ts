import { Router, type IRouter } from "express";

const router: IRouter = Router();

router.get("/streamlit-url", async (req, res): Promise<void> => {
  const replDomain = process.env.REPLIT_DEV_DOMAIN;
  const streamlitUrl = process.env.STREAMLIT_URL ?? "/streamlit";

  if (replDomain) {
    res.json({
      url: `https://${replDomain}/streamlit`,
      available: true,
    });
  } else {
    res.json({
      url: streamlitUrl,
      available: true,
    });
  }
});

export default router;
