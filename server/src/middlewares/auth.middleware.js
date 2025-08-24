import { sendResponse } from "../utils/apiResonse.js";
import { asyncHandler } from "../utils/asyncHandler.js";
import jwt from "jsonwebtoken";
import { statusType } from "../utils/statusType.js"; // Make sure this is correctly imported
import User from "../models/user.js";

export const verifyJWT = asyncHandler(async (req, res, next) => {
    const token = req.cookies?.accessToken || req.header("Authorization")?.replace("Bearer ", "");
    // console.log("Token being verified:", token);
    // console.log("Secret being used:", process.env.ACCESS_TOKEN_SECRET);

    if (!token) {
        return sendResponse(
            res,
            false,
            null,
            "Unauthorized request: Token missing",
            statusType.UNAUTHORIZED
        );
    }

    try {
        const decodedToken = jwt.verify(token, process.env.ACCESS_TOKEN_SECRET);

        // const user = await User.findById(decodedToken?._id).select(
        //   "-password -refreshToken"
        // );
        const user = await User.findById(decodedToken?.user_id).select("-password");

        if (!user) {
            return sendResponse(
                res,
                false,
                null,
                "Unauthorized request: Invalid access token",
                statusType.UNAUTHORIZED
            );
        }

        req.user = user;
        next();
    } catch (error) {
        return sendResponse(
            res,
            false,
            null,
            error?.message || "Unauthorized request: Token verification failed",
            statusType.UNAUTHORIZED
        );
    }
});
