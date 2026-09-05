import assert from "node:assert/strict"
import test from "node:test"
import { collectGitInfo, type GitRunner } from "./git-info.ts"

/** Builds a runner answering from a map keyed by the joined git arguments. */
function fakeGit(answers: Record<string, string | Error>): GitRunner {
	return async (args) => {
		const answer = answers[args.join(" ")]
		if (answer === undefined) throw new Error(`unexpected git call: git ${args.join(" ")}`)
		if (answer instanceof Error) throw answer
		return answer
	}
}

const FULL = {
	"rev-parse --show-toplevel": "/work/repo/main",
	"branch --show-current": "main",
	"rev-parse HEAD": "0123456789abcdef0123456789abcdef01234567",
	"remote get-url origin": "https://github.com/llucax/example.git",
}

test("collectGitInfo returns every field for a normal checkout", async () => {
	assert.deepEqual(await collectGitInfo("/work/repo/main", fakeGit(FULL)), {
		root: "/work/repo/main",
		branch: "main",
		commit: "0123456789abcdef0123456789abcdef01234567",
		origin: "https://github.com/llucax/example.git",
	})
})

test("collectGitInfo returns undefined outside a repository", async () => {
	const info = await collectGitInfo("/tmp", fakeGit({ "rev-parse --show-toplevel": new Error("not a git repository") }))
	assert.equal(info, undefined)
})

test("collectGitInfo returns undefined when git itself is missing", async () => {
	const info = await collectGitInfo("/work/repo/main", async () => {
		throw Object.assign(new Error("spawn git ENOENT"), { code: "ENOENT" })
	})
	assert.equal(info, undefined)
})

test("collectGitInfo omits the branch on a detached HEAD", async () => {
	const info = await collectGitInfo("/work/repo/main", fakeGit({ ...FULL, "branch --show-current": "" }))
	assert.ok(info)
	assert.equal(info.branch, undefined)
	assert.equal(info.commit, FULL["rev-parse HEAD"])
})

test("collectGitInfo omits the commit before the first commit", async () => {
	const info = await collectGitInfo(
		"/work/repo/main",
		fakeGit({ ...FULL, "rev-parse HEAD": new Error("ambiguous argument 'HEAD'") }),
	)
	assert.deepEqual(info, {
		root: "/work/repo/main",
		branch: "main",
		origin: FULL["remote get-url origin"],
	})
})

test("collectGitInfo omits the origin when there is no such remote", async () => {
	const info = await collectGitInfo(
		"/work/repo/main",
		fakeGit({ ...FULL, "remote get-url origin": new Error("No such remote 'origin'") }),
	)
	assert.ok(info)
	assert.equal(info.origin, undefined)
	assert.equal(info.root, "/work/repo/main")
})

test("collectGitInfo runs git in the directory it was given", async () => {
	const seen: string[] = []
	await collectGitInfo("/work/repo/topic", async (args, cwd) => {
		seen.push(cwd)
		return FULL[args.join(" ") as keyof typeof FULL]
	})
	assert.deepEqual(new Set(seen), new Set(["/work/repo/topic"]))
})
