import express from "express";
import cors from "cors";
import cookieParser from "cookie-parser";
import { userRoute } from "./controllers/user/userRoutes.js";
// import roleRouter from "./controllers/roles/rolesRouter.js"
import chatRouter from "./controllers/chats/chatRoutes.js";
import subscriptionRouter from "./controllers/subscription/subscriptionRoutes.js";
import promptRouter from "./controllers/ai/promptRoutes.js";
import { verifyJWT } from "./middlewares/auth.middleware.js";
const app = express();

app.use(
    cors({
        origin: ["http://localhost:3000"],
        credentials: true
    })
);

app.use(express.json({ limit: "50mb" }));
app.use(express.urlencoded({ extended: true, limit: "50mb" }));
app.use(express.static("public"));
app.use(cookieParser());

app.use("/api/users", userRoute);
// Public subscription routes
app.use("/api/subscription", subscriptionRouter);

// app.use("/api/role",roleRouter)
app.use(verifyJWT);
app.use("/api/sections", chatRouter);
app.use("/api/ai", promptRouter);

// backend route for OAuth callback
app.get("/oauth2callback", (req, res) => {
    // This endpoint should redirect to the frontend callback page with the token
    const token = req.query.access_token;
    if (token) {
        res.redirect(`${process.env.FRONTEND_URL}/oauth-callback#access_token=${token}`);
    } else {
        res.redirect(`${process.env.FRONTEND_URL}/oauth-callback#error=auth_failed`);
    }
});

export { app };
