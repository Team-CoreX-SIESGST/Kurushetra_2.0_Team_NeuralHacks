import User from "../../models/user.js";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";
import {
    asyncHandler,
    uploadOnCloudinary,
    deleteOnCloudinary,
    statusType,
    sendResponse
} from "../../utils/index.js";
import { verifyGoogleToken } from "../../utils/googleAuth.js";

// Token generator functions
const generateAccessToken = (user) => {
    return jwt.sign(
        { user_id: user._id, date_of_birth: user.date_of_birth },
        process.env.ACCESS_TOKEN_SECRET,
        { expiresIn: "1d" }
    );
};

const generateRefreshToken = (user) => {
    return jwt.sign(
        {
            user_id: user._id,
            date_of_birth: user.date_of_birth,
            token_version: user.token_version || 0
        },
        process.env.REFRESH_TOKEN_SECRET,
        { expiresIn: "7d" }
    );
};

const cookieOptions = {
    httpOnly: false,
    secure: true,
    sameSite: "Strict"
};

export const createUser = asyncHandler(async (req, res) => {
    const { name, email, password, date_of_birth, image, googleToken } = req.body;
    // Google Auth Flow
    console.log("hihfei");

    if (googleToken) {
        try {
            console.log("hihfei");
            const googleUser = await verifyGoogleToken(googleToken);
            let user = await User.findOne({
                $or: [{ email: googleUser.email }, { googleId: googleUser.sub }]
            });

            if (user) {
                return sendResponse(
                    res,
                    false,
                    null,
                    "User already exists",
                    statusType.BAD_REQUEST
                );
            }

            // Create new user with Google data
            user = await User.create({
                name: googleUser.name,
                email: googleUser.email,
                googleId: googleUser.sub,
                image: googleUser.picture,
                date_of_birth: date_of_birth || null
            });

            // Generate tokens and respond
            const accessToken = generateAccessToken(user);
            const refreshToken = generateRefreshToken(user);

            user.refresh_token = refreshToken;
            await user.save();

            const userData = user.toObject();
            delete userData.password;

            res.cookie("accessToken", accessToken, cookieOptions);
            res.cookie("refreshToken", refreshToken, cookieOptions);

            return sendResponse(
                res,
                true,
                { ...userData, accessToken },
                "User registered with Google",
                statusType.CREATED
            );
        } catch (error) {
            return sendResponse(res, false, null, error.message, statusType.BAD_REQUEST);
        }
    } else {
        if (!name || !email || !password) {
            return sendResponse(res, false, null, "Fields cannot be empty", statusType.BAD_REQUEST);
        }
        // if (req.files && req.files.image) {
        //     const avatarLocalPath = req.files.image[0].path;
        //     const image_temp = await uploadOnCloudinary(avatarLocalPath, { secure: true });
        //     image = image_temp?.secure_url;
        // }

        let user = await User.findOne({ email });
        if (user) {
            return sendResponse(
                res,
                false,
                null,
                "User already exists, please login",
                statusType.BAD_REQUEST
            );
        }

        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(password, salt);

        // Save User
        user = await User.create({ name, email, password: hashedPassword, date_of_birth, image });

        // Generate Tokens
        const accessToken = generateAccessToken(user);
        const refreshToken = generateRefreshToken(user);

        // Store refreshToken in DB
        user.refresh_token = refreshToken;
        await user.save();

        // Prepare response
        const userData = user.toObject();
        delete userData.password;
        // delete userData.refresh_token;

        res.cookie("accessToken", accessToken, cookieOptions);
        res.cookie("refreshToken", refreshToken, {
            ...cookieOptions,
            maxAge: 7 * 24 * 60 * 60 * 1000
        }); // 7 days
        return sendResponse(
            res,
            true,
            { ...userData, accessToken },
            "User registered successfully",
            statusType.CREATED
        );
    }
});

export const loginUser = asyncHandler(async (req, res) => {
    const { email, password, googleToken } = req.body;
    if (googleToken) {
        try {
            const googleUser = await verifyGoogleToken(googleToken);

            let user = await User.findOne({
                $or: [{ email: googleUser.email }, { googleId: googleUser.sub }]
            });

            // Auto-register if user doesn't exist
            if (!user) {
                user = await User.create({
                    name: googleUser.name,
                    email: googleUser.email,
                    googleId: googleUser.sub,
                    image: googleUser.picture
                });
            }

            // Generate tokens and respond
            const accessToken = generateAccessToken(user);
            const refreshToken = generateRefreshToken(user);

            user.refresh_token = refreshToken;
            await user.save();

            const userData = user.toObject();
            delete userData.password;

            res.cookie("accessToken", accessToken, cookieOptions);
            res.cookie("refreshToken", refreshToken, cookieOptions);

            return sendResponse(
                res,
                true,
                { ...userData, accessToken },
                "Login with Google Successful",
                statusType.OK
            );
        } catch (error) {
            return sendResponse(res, false, null, error.message, statusType.BAD_REQUEST);
        }
    } else {
        if (!email || !password) {
            return sendResponse(
                res,
                false,
                null,
                "Email and Password are required",
                statusType.BAD_REQUEST
            );
        }

        const user = await User.findOne({ email });
        if (!user) {
            return sendResponse(res, false, null, "User does not exist", statusType.BAD_REQUEST);
        }

        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) {
            return sendResponse(
                res,
                false,
                null,
                "Email or Password is incorrect",
                statusType.BAD_REQUEST
            );
        }

        const accessToken = generateAccessToken(user);
        const refreshToken = generateRefreshToken(user);

        user.refresh_token = refreshToken;
        await user.save();

        const userData = user.toObject();
        delete userData.password;
        // delete userData.refresh_token;
        res.cookie("accessToken", accessToken, cookieOptions);
        res.cookie("refreshToken", refreshToken, cookieOptions);

        return sendResponse(
            res,
            true,
            { ...userData, accessToken },
            "Login Successful",
            statusType.OK
        );
    }
});

export const getUser = asyncHandler(async (req, res) => {
    const user = req.user;

    if (!user) {
        return sendResponse(res, false, null, "User not found", statusType.NOT_FOUND);
    }

    return sendResponse(res, true, user, "User retrieved successfully", statusType.OK);
});

export const logoutUser = asyncHandler(async (req, res) => {
    await User.findByIdAndUpdate(
        req.user._id,
        {
            $unset: { refresh_token: 1 },
            $inc: { token_version: 1 }
        },
        { new: true }
    );

    return sendResponse(res, true, null, "User logged out successfully", statusType.OK);
});
