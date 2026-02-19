'use server';

import { revalidatePath } from 'next/cache';

/**
 * Revalidates all dashboard routes so that navigating to overview or analytics
 * after a task mutation always shows fresh data (clears Next.js Router Cache).
 */
export async function revalidateDashboard() {
  revalidatePath('/dashboard', 'page');
  revalidatePath('/dashboard/analytics', 'page');
  revalidatePath('/dashboard/tasks', 'page');
}
