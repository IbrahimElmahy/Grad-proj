import { useState } from "react";
import { motion } from "framer-motion";
import { useAuthStore } from "../store/authStore";
import { useAppStore } from "../store/appStore";
import { authService } from "../services/api";

export default function Settings() {
  // =========================
  // Auth Store & States
  // =========================

  const user = useAuthStore((state) => state.user);
  const login = useAuthStore((state) => state.login);
  const token = useAuthStore((state) => state.token);

  // App Store for global preferences
  const darkMode = useAppStore((state) => state.darkMode);
  const toggleDarkMode = useAppStore((state) => state.toggleDarkMode);
  const language = useAppStore((state) => state.language);
  const setLanguage = useAppStore((state) => state.setLanguage);

  const [criticalAlerts, setCriticalAlerts] = useState(true);
  const [weeklyReports, setWeeklyReports] = useState(true);
  const [systemUpdates, setSystemUpdates] = useState(false);
  const [timezone, setTimezone] = useState("UTC (Coordinated Universal Time)");

  // Profile
  const [showEditModal, setShowEditModal] = useState(false);
  const [name, setName] = useState(user?.name || "Captain Miller");
  const [email, setEmail] = useState(user?.email || "miller.safety@rvms-aviation.com");
  const [department, setDepartment] = useState(user?.airport || "Operations & Safety");

  // Password
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  // =========================
  // Handlers
  // =========================

  const handlePasswordUpdate = async () => {
    if (!currentPassword || !newPassword || !confirmPassword) {
      alert("Please fill all password fields");
      return;
    }

    if (newPassword !== confirmPassword) {
      alert("Passwords do not match");
      return;
    }

    if (newPassword.length < 6) {
      alert("New password must be at least 6 characters long");
      return;
    }

    try {
      const response = await authService.changePassword({
        email: user?.email || "",
        current_password: currentPassword,
        new_password: newPassword,
        confirm_new_password: confirmPassword,
      });
      alert(response.data?.message || "Password Updated Successfully");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (error) {
      console.error("Change password error:", error);
      alert(error.response?.data?.detail || "Failed to update password");
    }
  };

  const handleSaveProfile = () => {
    login({
      user: {
        ...user,
        name,
        email,
        airport: department,
      },
      token,
    });
    alert("Profile Updated Successfully");
    setShowEditModal(false);
  };

  // =========================
  // UI
  // =========================

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-6"
    >
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-800">
          Account Settings
        </h1>

        <p className="text-slate-500 mt-1">
          Manage your profile and system
          preferences.
        </p>
      </div>

      {/* ========================= */}
      {/* Profile Card */}
      {/* ========================= */}

      <div className="bg-white border border-slate-200 rounded-3xl p-6 mb-6 shadow-sm">
        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-5">
          {/* Left */}
          <div className="flex items-center gap-5">
            {/* Avatar */}
            <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-orange-400 to-red-500 flex items-center justify-center text-3xl font-bold text-white shadow-lg">
              CM
            </div>

            {/* Info */}
            <div>
              <p className="text-slate-400 text-xs uppercase tracking-widest">
                Full Name
              </p>

              <h2 className="font-bold text-2xl text-slate-800 mt-1">
                {name}
              </h2>

              <p className="text-green-600 text-sm mt-2 font-medium">
                ● Safety Officer
              </p>
            </div>
          </div>

          {/* Edit */}
          <button
            onClick={() =>
              setShowEditModal(true)
            }
            className="px-5 py-2.5 rounded-2xl bg-brand-500 hover:bg-brand-600 text-white transition font-medium text-sm shadow-sm"
          >
            Edit Profile
          </button>
        </div>

        {/* Info Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
          <div>
            <p className="text-slate-400 text-xs uppercase tracking-widest">
              Email Address
            </p>

            <p className="mt-2 font-medium text-slate-700">
              {email}
            </p>
          </div>

          <div>
            <p className="text-slate-400 text-xs uppercase tracking-widest">
              Department
            </p>

            <p className="mt-2 font-medium text-slate-700">
              {department}
            </p>
          </div>
        </div>
      </div>

      {/* ========================= */}
      {/* Notifications */}
      {/* ========================= */}

      <div className="bg-white border border-slate-200 rounded-3xl p-6 mb-6 shadow-sm">
        <h2 className="text-xl font-bold text-slate-800 mb-6">
          Email Notifications
        </h2>

        <div className="space-y-7">
          {/* Critical Alerts */}
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-slate-800">
                Critical Alerts
              </h3>

              <p className="text-slate-500 text-sm mt-1">
                Immediate email for runway
                visibility drops below threshold.
              </p>
            </div>

            <button
              onClick={() =>
                setCriticalAlerts(
                  !criticalAlerts
                )
              }
              className={`w-14 h-7 rounded-full relative transition-all ${
                criticalAlerts
                  ? "bg-brand-500"
                  : "bg-slate-300"
              }`}
            >
              <span
                className={`absolute top-1 w-5 h-5 bg-white rounded-full transition-all ${
                  criticalAlerts
                    ? "right-1"
                    : "left-1"
                }`}
              />
            </button>
          </div>

          {/* Weekly Reports */}
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-slate-800">
                Weekly Reports
              </h3>

              <p className="text-slate-500 text-sm mt-1">
                Summary of system performance and
                history logs.
              </p>
            </div>

            <button
              onClick={() =>
                setWeeklyReports(
                  !weeklyReports
                )
              }
              className={`w-14 h-7 rounded-full relative transition-all ${
                weeklyReports
                  ? "bg-brand-500"
                  : "bg-slate-300"
              }`}
            >
              <span
                className={`absolute top-1 w-5 h-5 bg-white rounded-full transition-all ${
                  weeklyReports
                    ? "right-1"
                    : "left-1"
                }`}
              />
            </button>
          </div>

          {/* System Updates */}
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-slate-800">
                System Updates
              </h3>

              <p className="text-slate-500 text-sm mt-1">
                Notices about maintenance and
                software improvements.
              </p>
            </div>

            <button
              onClick={() =>
                setSystemUpdates(
                  !systemUpdates
                )
              }
              className={`w-14 h-7 rounded-full relative transition-all ${
                systemUpdates
                  ? "bg-brand-500"
                  : "bg-slate-300"
              }`}
            >
              <span
                className={`absolute top-1 w-5 h-5 bg-white rounded-full transition-all ${
                  systemUpdates
                    ? "right-1"
                    : "left-1"
                }`}
              />
            </button>
          </div>
        </div>
      </div>

      {/* ========================= */}
      {/* Password */}
      {/* ========================= */}

      <div className="bg-white border border-slate-200 rounded-3xl p-6 mb-6 shadow-sm">
        <h2 className="text-xl font-bold text-slate-800 mb-6">
          Change Password
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Current */}
          <input
            type="password"
            placeholder="Current Password"
            value={currentPassword}
            onChange={(e) =>
              setCurrentPassword(
                e.target.value
              )
            }
            className="bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 outline-none focus:ring-2 focus:ring-brand-500"
          />

          {/* New */}
          <input
            type="password"
            placeholder="New Password"
            value={newPassword}
            onChange={(e) =>
              setNewPassword(
                e.target.value
              )
            }
            className="bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 outline-none focus:ring-2 focus:ring-brand-500"
          />

          {/* Confirm */}
          <input
            type="password"
            placeholder="Confirm Password"
            value={confirmPassword}
            onChange={(e) =>
              setConfirmPassword(
                e.target.value
              )
            }
            className="bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 outline-none focus:ring-2 focus:ring-brand-500"
          />
        </div>

        <button
          onClick={handlePasswordUpdate}
          className="mt-5 px-5 py-3 rounded-2xl bg-brand-500 hover:bg-brand-600 text-white transition font-medium shadow-sm"
        >
          Update Password
        </button>
      </div>

      {/* ========================= */}
      {/* Preferences */}
      {/* ========================= */}

      <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm">
        <h2 className="text-xl font-bold text-slate-800 mb-6">
          System Preferences
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Language */}
          <div>
            <label className="block text-slate-500 text-sm mb-2">
              Language
            </label>

            <select
              value={language}
              onChange={(e) =>
                setLanguage(
                  e.target.value
                )
              }
              className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 outline-none focus:ring-2 focus:ring-brand-500"
            >
              <option>
                English (US)
              </option>

              <option>Arabic</option>

              <option>French</option>
            </select>
          </div>

          {/* Timezone */}
          <div>
            <label className="block text-slate-500 text-sm mb-2">
              Timezone
            </label>

            <select
              value={timezone}
              onChange={(e) =>
                setTimezone(
                  e.target.value
                )
              }
              className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 outline-none focus:ring-2 focus:ring-brand-500"
            >
              <option>
                UTC (Coordinated Universal
                Time)
              </option>

              <option>
                GMT+2 Cairo
              </option>

              <option>
                GMT+1 Paris
              </option>
            </select>
          </div>
        </div>

        {/* Dark Mode */}
        <div className="mt-8 p-5 rounded-3xl bg-slate-50 border border-slate-200 flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-slate-800">
              Dark Mode
            </h3>

            <p className="text-slate-500 text-sm mt-1">
              Reduce eye strain during night
              shifts.
            </p>

            <p className="text-blue-500 text-sm mt-3">
              ☀ System is currently in{" "}
              {darkMode
                ? "Dark"
                : "Light"}{" "}
              Mode
            </p>
          </div>

          <button
            onClick={toggleDarkMode}
            className={`w-14 h-7 rounded-full relative transition-all ${
              darkMode
                ? "bg-brand-500"
                : "bg-slate-300"
            }`}
          >
            <span
              className={`absolute top-1 w-5 h-5 bg-white rounded-full transition-all ${
                darkMode
                  ? "right-1"
                  : "left-1"
              }`}
            />
          </button>
        </div>
      </div>

      {/* ========================= */}
      {/* Footer */}
      {/* ========================= */}

      <div className="text-center text-slate-400 text-sm mt-8">
        © 2026 RVMS Aviation Monitoring
        System. All rights reserved.
      </div>

      {/* ========================= */}
      {/* Edit Modal */}
      {/* ========================= */}

      {showEditModal && (
        <div className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
          <div className="bg-white rounded-[32px] w-full max-w-lg p-7 shadow-2xl">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-slate-800">
                Edit Profile
              </h2>

              <button
                onClick={() =>
                  setShowEditModal(false)
                }
                className="text-slate-400 hover:text-slate-600 text-xl"
              >
                ✕
              </button>
            </div>

            {/* Avatar */}
            <div className="flex justify-center mb-6">
              <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-orange-400 to-red-500 flex items-center justify-center text-3xl font-bold text-white shadow-lg">
                CM
              </div>
            </div>

            {/* Inputs */}
            <div className="space-y-5">
              {/* Name */}
              <div>
                <label className="block text-sm text-slate-500 mb-2">
                  Full Name
                </label>

                <input
                  type="text"
                  value={name}
                  onChange={(e) =>
                    setName(
                      e.target.value
                    )
                  }
                  className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>

              {/* Email */}
              <div>
                <label className="block text-sm text-slate-500 mb-2">
                  Email Address
                </label>

                <input
                  type="email"
                  value={email}
                  onChange={(e) =>
                    setEmail(
                      e.target.value
                    )
                  }
                  className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>

              {/* Department */}
              <div>
                <label className="block text-sm text-slate-500 mb-2">
                  Department
                </label>

                <input
                  type="text"
                  value={department}
                  onChange={(e) =>
                    setDepartment(
                      e.target.value
                    )
                  }
                  className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-3 mt-8">
              <button
                onClick={() =>
                  setShowEditModal(false)
                }
                className="px-5 py-3 rounded-2xl border border-slate-200 text-slate-600 hover:bg-slate-50"
              >
                Cancel
              </button>

              <button
                onClick={handleSaveProfile}
                className="px-5 py-3 rounded-2xl bg-brand-500 hover:bg-brand-600 text-white font-medium"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
}