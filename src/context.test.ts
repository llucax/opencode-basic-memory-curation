import assert from "node:assert/strict"
import test from "node:test"
import { AUTHOR_ENV_VAR } from "./author.ts"
import { buildSessionContext, formatSessionContext, type SessionContext } from "./context.ts"
import type { GitRunner } from "./git-info.ts"

const INPUT = {
	sessionID: "ses_f8e679d93ffeQ37ZeqQvhUKpNv",
	directory: "/work/repo/main",
	worktree: "/work/repo/main",
}

const GIT_ANSWERS: Record<string, string> = {
	"rev-parse --show-toplevel": "/work/repo/main",
	"branch --show-current": "main",
	"rev-parse HEAD": "0123456789abcdef0123456789abcdef01234567",
	"remote get-url origin": "https://github.com/llucax/example.git",
}

const fakeGit: GitRunner = async (args) => {
	const answer = GIT_ANSWERS[args.join(" ")]
	if (answer === undefined) throw new Error(`unexpected git call: git ${args.join(" ")}`)
	return answer
}

const noGit: GitRunner = async () => {
	throw new Error("not a git repository")
}

test("buildSessionContext returns the documented shape with git enrichment", async () => {
	const result = await buildSessionContext(INPUT, {}, { run: fakeGit, env: { [AUTHOR_ENV_VAR]: "llucax" } })
	assert.deepEqual(result, {
		session_id: INPUT.sessionID,
		author: "llucax",
		directory: INPUT.directory,
		worktree: INPUT.worktree,
		git: {
			root: "/work/repo/main",
			branch: "main",
			commit: "0123456789abcdef0123456789abcdef01234567",
			origin: "https://github.com/llucax/example.git",
		},
	})
})

test("buildSessionContext omits git entirely outside a repository", async () => {
	const result = await buildSessionContext(INPUT, {}, { run: noGit, env: { [AUTHOR_ENV_VAR]: "llucax" } })
	assert.deepEqual(result, {
		session_id: INPUT.sessionID,
		author: "llucax",
		directory: INPUT.directory,
		worktree: INPUT.worktree,
	})
	assert.ok(!("git" in result), "the git key must be absent, not null")
})

test("buildSessionContext takes the author from the opencode config when the environment has none", async () => {
	const result = await buildSessionContext(INPUT, { username: "llucax" }, { run: noGit, env: {} })
	assert.equal((result as SessionContext).author, "llucax")
})

test("buildSessionContext reports an error instead of a context when no author is configured", async () => {
	const result = await buildSessionContext(INPUT, {}, { run: fakeGit, env: {} })
	assert.ok("error" in result)
	assert.ok(result.error.includes(AUTHOR_ENV_VAR))
	assert.ok(result.error.includes("username"))
})

test("formatSessionContext emits JSON with the keys in the documented order", async () => {
	const result = await buildSessionContext(INPUT, {}, { run: fakeGit, env: { [AUTHOR_ENV_VAR]: "llucax" } })
	const text = formatSessionContext(result)
	assert.deepEqual(Object.keys(JSON.parse(text)), ["session_id", "author", "directory", "worktree", "git"])
})

test("formatSessionContext passes the error through as a plain line", () => {
	assert.equal(formatSessionContext({ error: "boom" }), "boom")
})
