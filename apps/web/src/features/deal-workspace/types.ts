export type WorkspaceStage =
    | "intake"
    | "research"
    | "buyers"
    | "offer"
    | "complete";

export interface WorkspaceState {
    stage: WorkspaceStage;

    title: string;

    description: string;

    progress: number;

    researchComplete: boolean;

    buyersFound: boolean;

    offerGenerated: boolean;
}