import type { PluginInput } from "@opencode-ai/plugin"

/** Fetches a session's creation time in epoch milliseconds, or undefined when the lookup fails. */
export type SessionTimeFetcher = (sessionID: string) => Promise<number | undefined>

/**
 * Builds a fetcher backed by the real opencode client, used by the plugin.
 * Fails soft: any thrown error, or a response carrying no data, resolves to
 * undefined instead of throwing, so a transient lookup failure costs the
 * tool only its `started_at` field, not the whole session context.
 */
export function makeSessionTimeFetcher(client: PluginInput["client"]): SessionTimeFetcher {
	return async (sessionID) => {
		try {
			const result = await client.session.get({ path: { id: sessionID } })
			return result.data?.time.created
		} catch {
			return undefined
		}
	}
}
