import { Router } from "express";
import { deleteUserData } from "./deleteUserController";
import { authMiddleware } from '../auth.middleware.js';

const deleteUserRouter = Router();
deleteUserData.delete('/delete-account', authMiddleware, deleteUserData);

export default deleteUserData;