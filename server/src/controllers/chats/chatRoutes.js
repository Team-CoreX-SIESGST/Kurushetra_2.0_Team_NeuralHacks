// routes/chatRoutes.js
import express from "express";
import {
    createSection,
    getSections,
    getSection,
    sendMessage,
    deleteSection,
    updateSectionTitle,
    uploadDocument,
    getSectionWithDocuments,
    deleteDocument
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

// Chat routes


// NEW: Document routes
router.post("/section/:sectionId/upload-document", uploadDocument);
router.get("/section/:sectionId/with-documents", getSectionWithDocuments);
router.delete("/document/:documentId", deleteDocument);

export default router;
