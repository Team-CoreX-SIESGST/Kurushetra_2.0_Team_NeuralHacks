import express from "express";
import { createRole, getAllRoles, deleteRole, getRole } from "./rolesController.js";

const router = express.Router();

router.post("/create", createRole);
router.get("/all", getAllRoles);
router.get("/:id", getRole);
router.delete("/:id", deleteRole);

export default router;
