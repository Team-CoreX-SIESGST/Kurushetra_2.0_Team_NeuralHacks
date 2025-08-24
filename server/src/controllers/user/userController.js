import User from "../../models/user.js";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";
import { asyncHandler,uploadOnCloudinary,deleteOnCloudinary,statusType,sendResponse } from "../../utils/index.js";

// Token generator functions
const generateAccessToken = (user) => {
    return jwt.sign(
        { user_id: user._id, role: user.role },
        process.env.ACCESS_TOKEN_SECRET,
        { expiresIn: "1d" }
    );
};

const generateRefreshToken = (user) => {
    return jwt.sign(
        {
            user_id: user._id,
            role: user.role,
            token_version: user.token_version || 0,
        },
        process.env.REFRESH_TOKEN_SECRET,
        { expiresIn: "7d" }
    );
};

const cookieOptions = {
    httpOnly: false,
    secure: true,
    sameSite: "Strict",
};

export const createUser = asyncHandler(async (req, res) => {
    const { name, email, password, role } = req.body;
    if (!name || !email || !password || !role) {
        return sendResponse(res, false, null, "Fields cannot be empty", statusType.BAD_REQUEST);
    }
    let image = null;
    if (req.files && req.files.image) {
        const avatarLocalPath = req.files.image[0].path;
        const image_temp = await uploadOnCloudinary(avatarLocalPath, { secure: true });
        image = image_temp?.secure_url;
    }

    let user = await User.findOne({ email });
    if (user) {
        return sendResponse(res, false, null, "User already exists, please login", statusType.BAD_REQUEST);
    }

    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(password, salt);

    // Save User
    user = await User.create({ name, email, password: hashedPassword, role, image });

    // Generate Tokens
    const accessToken = generateAccessToken(user);
    const refreshToken = generateRefreshToken(user);

    // Store refreshToken in DB
    user.refresh_token = refreshToken;
    await user.save();

    // Prepare response
    const userData = user.toObject();
    delete userData.pin;
    delete userData.refresh_token;

    return sendResponse(res, true,userData,"User registered successfully",statusType.CREATED);
});

export const loginUser = asyncHandler(async (req, res) => {
    const { email, password } = req.body;

    if (!email || !password) {
        return sendResponse(res, false, null, "Email and Password are required", statusType.BAD_REQUEST);
    }

    const user = await User.findOne({ email });
    if (!user) {
        return sendResponse(res, false, null, "User does not exist", statusType.BAD_REQUEST);
    }

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
        return sendResponse(res, false, null, "Email or Password is incorrect", statusType.BAD_REQUEST);
    }

    const accessToken = generateAccessToken(user);
    const refreshToken = generateRefreshToken(user);

    user.refresh_token = refreshToken;
    await user.save();

    const userData = user.toObject();
    delete userData.password;
    delete userData.refresh_token;

    return sendResponse(res,true,userData,"Login Successful",statusType.OK)
});

