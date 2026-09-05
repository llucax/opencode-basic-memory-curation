import assert from "node:assert/strict"
import test from "node:test"
import { AUTHOR_ENV_VAR, MISSING_AUTHOR_MESSAGE, resolveAuthor } from "./author.ts"

test("resolveAuthor prefers the environment variable over the config username", () => {
	const author = resolveAuthor({ username: "config-name" }, { [AUTHOR_ENV_VAR]: "env-name" })
	assert.equal(author, "env-name")
})

test("resolveAuthor falls back to the config username", () => {
	assert.equal(resolveAuthor({ username: "config-name" }, {}), "config-name")
})

test("resolveAuthor trims surrounding whitespace", () => {
	assert.equal(resolveAuthor({}, { [AUTHOR_ENV_VAR]: "  spaced  " }), "spaced")
	assert.equal(resolveAuthor({ username: " padded " }, {}), "padded")
})

test("resolveAuthor treats a blank value as unset and keeps looking", () => {
	assert.equal(resolveAuthor({ username: "config-name" }, { [AUTHOR_ENV_VAR]: "   " }), "config-name")
	assert.equal(resolveAuthor({ username: "  " }, {}), undefined)
})

test("resolveAuthor returns undefined rather than guessing from the environment", () => {
	// $USER and git's user.name are deliberately not consulted.
	assert.equal(resolveAuthor({}, { USER: "luca", LOGNAME: "luca" }), undefined)
})

test("the missing-author message mentions both settings that can provide it", () => {
	assert.ok(MISSING_AUTHOR_MESSAGE.includes(AUTHOR_ENV_VAR), "must mention the environment variable")
	assert.ok(MISSING_AUTHOR_MESSAGE.includes("username"), "must mention the config field")
})
