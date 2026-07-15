import { api } from "../lib/api";
import type { ShareIntake, ShareIntakeCreate } from "../types/shareIntake";

export const createShareIntake = (data: ShareIntakeCreate) =>
  api.post<ShareIntake>("/share-intake", data);

export const getShareIntake = (shareId: string) =>
  api.get<ShareIntake>(`/share-intake/${shareId}`);

export const processShareIntake = (shareId: string) =>
  api.post<ShareIntake>(`/share-intake/${shareId}/process`);
