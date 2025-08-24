// routes/chatRoutes.js
import express from "express";
import {
    createSection,
    getSections,
    getSection,
    sendMessage,
    deleteSection,
    updateSectionTitle
} from "./chatController.js";
import { chatLimiter } from "../../utils/index.js";
const router = express.Router();

// All routes require authentication
// router.use(verifyToken);

router.post("/", createSection);
router.get("/", getSections);
router.get("/:sectionId", getSection);
router.post("/:sectionId/message", chatLimiter, sendMessage);
router.put("/:sectionId/title", updateSectionTitle);
router.delete("/:sectionId", deleteSection);

export default router;
