import { type ConfigLike, MISSING_AUTHOR_MESSAGE, resolveAuthor } from "./author.ts"
import { collectGitInfo, type GitInfo, type GitRunner } from "./git-info.ts"

/** The JSON payload the tool returns. Field names are snake_case, as the plan specifies. */
export interface SessionContext {
	session_id: string
	author: string
	directory: string
	worktree: string
	git?: GitInfo
}

/** The slice of opencode's tool context this module needs. */
export interface SessionContextInput {
	sessionID: string
	directory: string
	worktree: string
}

export interface BuildSessionContextOptions {
	/** Overrides how git is invoked, for tests. */
	run?: GitRunner
	/** Overrides the environment author lookup, for tests. */
	env?: NodeJS.ProcessEnv
}

/**
 * Builds the provenance record for the current session. Returns the error
 * message instead of a context when no author is configured, because a
 * session record whose author is a guess is worse than none: notes carrying
 * it may be read by other people long after the session is gone.
 */
export async function buildSessionContext(
	input: SessionContextInput,
	config: ConfigLike = {},
	options: BuildSessionContextOptions = {},
): Promise<SessionContext | { error: string }> {
	const author = resolveAuthor(config, options.env)
	if (!author) return { error: MISSING_AUTHOR_MESSAGE }

	const context: SessionContext = {
		session_id: input.sessionID,
		author,
		directory: input.directory,
		worktree: input.worktree,
	}

	const git = await collectGitInfo(input.directory, options.run)
	if (git) context.git = git
	return context
}

/** Renders a built context as the tool's return value: pretty JSON, or the plain error line. */
export function formatSessionContext(result: SessionContext | { error: string }): string {
	if ("error" in result) return result.error
	return JSON.stringify(result, null, 2)
}
