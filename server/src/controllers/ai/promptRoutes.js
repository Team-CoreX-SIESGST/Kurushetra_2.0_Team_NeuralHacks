import { Router } from "express";
import { improvePrompt, suggestPromptStructure } from "./promptController.js";

const promptRouter = Router();

// Improve user's prompt
promptRouter.post("/improve", improvePrompt);

// Suggest prompt structure for a topic
promptRouter.post("/suggest-structure", suggestPromptStructure);

export default promptRouter;
