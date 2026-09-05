import { execFile } from "node:child_process"
import { promisify } from "node:util"

const execFileAsync = promisify(execFile)

const TIMEOUT_MS = 5_000
const MAX_BUFFER_BYTES = 1024 * 1024

/** Git facts about the checkout a session is working in. Every field is optional. */
export interface GitInfo {
	root?: string
	branch?: string
	commit?: string
	origin?: string
}

/** Runs `git <args>` in `cwd` and resolves its trimmed stdout, or rejects. */
export type GitRunner = (args: readonly string[], cwd: string) => Promise<string>

export const runGit: GitRunner = async (args, cwd) => {
	const { stdout } = await execFileAsync("git", [...args], {
		cwd,
		timeout: TIMEOUT_MS,
		maxBuffer: MAX_BUFFER_BYTES,
	})
	return stdout.trim()
}

async function tryGit(run: GitRunner, args: readonly string[], cwd: string): Promise<string | undefined> {
	try {
		const output = await run(args, cwd)
		return output || undefined
	} catch {
		return undefined
	}
}

/**
 * Collects cheap git provenance for `directory`, or undefined when it is not
 * a repository, git is missing, or the repository root cannot be read. Every
 * individual field fails soft on its own: a detached HEAD has no branch, a
 * repository with no commit yet has no HEAD, and a checkout with no `origin`
 * remote has no origin, none of which should cost the caller the other
 * fields.
 *
 * In a worktree layout the root is the linked worktree's own directory, not
 * the shared bare store. That is deliberate: provenance should point at the
 * tree whose files the session actually read.
 */
export async function collectGitInfo(directory: string, run: GitRunner = runGit): Promise<GitInfo | undefined> {
	const root = await tryGit(run, ["rev-parse", "--show-toplevel"], directory)
	if (!root) return undefined

	// `branch --show-current` prints nothing on a detached HEAD and still
	// prints the branch name before the first commit, unlike `rev-parse
	// --abbrev-ref HEAD`, which fails outright on an unborn branch.
	const [branch, commit, origin] = await Promise.all([
		tryGit(run, ["branch", "--show-current"], directory),
		tryGit(run, ["rev-parse", "HEAD"], directory),
		tryGit(run, ["remote", "get-url", "origin"], directory),
	])

	const info: GitInfo = { root }
	if (branch) info.branch = branch
	if (commit) info.commit = commit
	if (origin) info.origin = origin
	return info
}
