import express from "express";
import { upload } from "../../middlewares/multer.middleware.js";

const userRoute = express.Router();

import { loginUser, createUser,getUser,logoutUser } from "./userController.js";
import { verifyJWT } from "../../middlewares/auth.middleware.js";

userRoute.get("/", (req, res) => {
    res.send("User details fetched");
});

userRoute.post("/create", createUser); // signup
userRoute.post("/login", loginUser); // login

userRoute.patch("/details", (req, res) => {
    res.send("User details updated");
});
userRoute.get("/get_user", verifyJWT, getUser); // Protected route
userRoute.post("/logout", verifyJWT, logoutUser); // Protected route
export { userRoute };
