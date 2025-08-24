import Role from "../../models/role.js";
import Role_Mapper from "../../models/role_mapper.js";
import { asyncHandler, sendResponse, statusType } from "../../utils/index.js";
import User from "../../models/user.js";
// Create Role
export const createRole = asyncHandler(async (req, res) => {
    const { role_name, permissions } = req.body;

    // Validate input
    if (!role_name || !permissions) {
        return sendResponse(
            res,
            false,
            null,
            "Role name and permissions are required",
            statusType.BAD_REQUEST
        );
    }

    // Check if role already exists
    const existingRole = await Role.findOne({ name: role_name.toLowerCase() });
    if (existingRole) {
        return sendResponse(res, false, null, "Role already exists", statusType.BAD_REQUEST);
    }

    // Create new role
    const role = await Role.create({ name: role_name.toLowerCase() });

    // Prepare role mapper entries
    const roleMappers = permissions.map((permission) => ({
        role_id: role._id,
        page: permission.page.toLowerCase(),
        read: permission.read || false,
        edit: permission.edit || false,
        delete: permission.delete || false,
        download: permission.download || false
    }));

    // Insert all permissions
    await Role_Mapper.insertMany(roleMappers);

    return sendResponse(
        res,
        true,
        null,
        "Role created successfully",
        statusType.CREATED
    );
});

// Get All Roles with Permissions
export const getAllRoles = asyncHandler(async (req, res) => {
    // Get all roles
    const roles = await Role.find({});

    // For each role, get its permissions
    const rolesWithPermissions = await Promise.all(
        roles.map(async (role) => {
            const permissions = await Role_Mapper.find({ role_id: role._id });
            return {
                role: role,
                permissions: permissions
            };
        })
    );

    return sendResponse(
        res,
        true,
        rolesWithPermissions,
        "Roles fetched successfully",
        statusType.OK
    );
});

// Delete Role
export const deleteRole = asyncHandler(async (req, res) => {
    const { id } = req.params;

    // Check if role exists
    const role = await Role.findById(id);
    if (!role) {
        return sendResponse(res, false, null, "Role not found", statusType.NOT_FOUND);
    }

    // Check if role is being used by any user
    const usersWithRole = await User.find({ role: role.name });

    if (usersWithRole.length > 0) {
        return sendResponse(
            res,
            false,
            null,
            "Cannot delete role. It is assigned to one or more users.",
            statusType.BAD_REQUEST
        );
    }

    // Delete role and its permissions (using transaction for atomicity)
    const session = await mongoose.startSession();
    session.startTransaction();

    try {
        await Role_Mapper.deleteMany({ role_id: id }).session(session);
        await Role.findByIdAndDelete(id).session(session);

        await session.commitTransaction();
        session.endSession();

        return sendResponse(res, true, null, "Role deleted successfully", statusType.OK);
    } catch (error) {
        await session.abortTransaction();
        session.endSession();

        return sendResponse(
            res,
            false,
            null,
            "Error deleting role",
            statusType.INTERNAL_SERVER_ERROR
        );
    }
});

// Get Single Role with Permissions
export const getRole = asyncHandler(async (req, res) => {
    const { id } = req.params;

    // Check if role exists
    const role = await Role.findById(id);
    if (!role) {
        return sendResponse(res, false, null, "Role not found", statusType.NOT_FOUND);
    }

    // Get role permissions
    const permissions = await Role_Mapper.find({ role_id: id });

    return sendResponse(
        res,
        true,
        { role, permissions },
        "Role fetched successfully",
        statusType.OK
    );
});
