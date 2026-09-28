import assert from "node:assert/strict"
import test from "node:test"
import type { PluginInput } from "@opencode-ai/plugin"
import { makeSessionTimeFetcher } from "./session-time.ts"

/** Builds a fake client exposing only the one call this module makes. */
function fakeClient(get: (input: { path: { id: string } }) => Promise<unknown>): PluginInput["client"] {
	return { session: { get } } as unknown as PluginInput["client"]
}

test("makeSessionTimeFetcher returns the session's creation time", async () => {
	const fetcher = makeSessionTimeFetcher(fakeClient(async () => ({ data: { time: { created: 1234567890000 } } })))
	assert.equal(await fetcher("ses_abc"), 1234567890000)
})

test("makeSessionTimeFetcher passes the session ID through as the path parameter", async () => {
	let seenID: string | undefined
	const fetcher = makeSessionTimeFetcher(
		fakeClient(async (input) => {
			seenID = input.path.id
			return { data: { time: { created: 1 } } }
		}),
	)
	await fetcher("ses_xyz")
	assert.equal(seenID, "ses_xyz")
})

test("makeSessionTimeFetcher returns undefined when the client reports an error instead of data", async () => {
	const fetcher = makeSessionTimeFetcher(fakeClient(async () => ({ error: { message: "not found" } })))
	assert.equal(await fetcher("ses_abc"), undefined)
})

test("makeSessionTimeFetcher returns undefined when the client throws", async () => {
	const fetcher = makeSessionTimeFetcher(
		fakeClient(async () => {
			throw new Error("network error")
		}),
	)
	assert.equal(await fetcher("ses_abc"), undefined)
})
