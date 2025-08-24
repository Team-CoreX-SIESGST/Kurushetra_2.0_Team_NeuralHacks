import express from "express";
import cors from "cors";
import cookieParser from "cookie-parser";
import { userRoute } from "./controllers/user/userRoutes.js";
import roleRouter from "./controllers/roles/rolesRouter.js"
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
app.use("/api/role",roleRouter)

export { app };
