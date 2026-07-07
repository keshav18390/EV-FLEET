"use client";

import { useQuery } from "@tanstack/react-query";
import { ShieldCheck } from "lucide-react";
import { Topbar } from "@/components/Topbar";
import { Card, Badge, LoadingState, ErrorState, EmptyState } from "@/components/ui";
import { useAuth } from "@/lib/auth-context";
import { api, friendlyError } from "@/lib/api";
import type { User } from "@/lib/types";

export default function AdminPage() {
  const { user } = useAuth();

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["admin-users"],
    queryFn: async () => (await api.get<User[]>("/api/admin/users")).data,
    enabled: user?.role === "admin",
  });

  if (user && user.role !== "admin") {
    return (
      <>
        <Topbar title="Admin Panel" />
        <ErrorState message="You need admin permissions to view this page." />
      </>
    );
  }

  return (
    <>
      <Topbar title="Admin Panel" />
      <main className="p-4 lg:p-8">
        <Card>
          <div className="px-5 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center gap-2">
            <ShieldCheck size={16} className="text-brand-600" />
            <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300">All Users</h3>
          </div>
          {isLoading ? (
            <LoadingState />
          ) : isError ? (
            <ErrorState message={friendlyError(error)} />
          ) : !data || data.length === 0 ? (
            <EmptyState message="No users found." />
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-slate-500 border-b border-slate-200 dark:border-slate-800">
                  <th className="px-4 py-3 font-medium">Name</th>
                  <th className="px-4 py-3 font-medium">Email</th>
                  <th className="px-4 py-3 font-medium">Role</th>
                </tr>
              </thead>
              <tbody>
                {data.map((u) => (
                  <tr key={u.id} className="border-b border-slate-100 dark:border-slate-800/60">
                    <td className="px-4 py-3 font-medium text-slate-900 dark:text-white">{u.full_name}</td>
                    <td className="px-4 py-3 text-slate-600 dark:text-slate-400">{u.email}</td>
                    <td className="px-4 py-3">
                      <Badge color={u.role === "admin" ? "red" : "blue"}>{u.role.replace("_", " ")}</Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </Card>
      </main>
    </>
  );
}
