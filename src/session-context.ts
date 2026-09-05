import type { Plugin } from "@opencode-ai/plugin"
import { tool } from "@opencode-ai/plugin"
import type { ConfigLike } from "./author.ts"
import { buildSessionContext, formatSessionContext } from "./context.ts"

/**
 * A file loaded as an opencode plugin must export only plugin factories: the
 * loader iterates every export and throws on the first one that is not a
 * function, taking every tool in the file down with it. Keep this file to
 * the single default export; put anything else in an imported module.
 *
 * This plugin registers one tool and nothing else. No event hooks, no
 * prompt or context injection, no memory calls of its own: it only answers
 * "which session, which developer, which checkout" when an agent explicitly
 * asks.
 */
export default (async () => {
	let lastConfig: ConfigLike = {}

	return {
		config: async (config) => {
			lastConfig = config
		},

		tool: {
			memory_session_context: tool({
				description:
					"Provenance for the current opencode session: session ID, configured author, directory, worktree and git position. Call this only when about to record session-derived evidence in Basic Memory, so the note can cite where the evidence came from. Do not call it routinely; it tells you nothing about the task itself.",
				args: {},
				async execute(_args, context) {
					try {
						const result = await buildSessionContext(
							{
								sessionID: context.sessionID,
								directory: context.directory,
								worktree: context.worktree,
							},
							lastConfig,
						)
						return formatSessionContext(result)
					} catch (error) {
						const message = error instanceof Error ? error.message : String(error)
						return `memory_session_context: ${message.split("\n")[0]}`
					}
				},
			}),
		},
	}
}) satisfies Plugin
