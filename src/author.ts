/** Environment variable holding the developer identity used for provenance. */
export const AUTHOR_ENV_VAR = "OPENCODE_MEMORY_AUTHOR"

/** The slice of the opencode config this module reads: just `username`. */
export interface ConfigLike {
	username?: string
}

/**
 * Returned when neither source is set. It states both settings by name
 * because the only useful reaction to a missing author is to configure one,
 * and the agent cannot see this repository's README.
 */
export const MISSING_AUTHOR_MESSAGE =
	`memory_session_context: no author configured. Set the ${AUTHOR_ENV_VAR} environment variable ` +
	`(a stable identity such as a GitHub handle or company email), or the "username" field in ` +
	`opencode's config (~/.config/opencode/opencode.json). The identity is never guessed from ` +
	`$USER or from git's user.name, because memory provenance has to point at a person on purpose.`

/**
 * Resolves the developer identity recorded as memory provenance. The
 * environment variable wins over the opencode config so a single shell can
 * override a machine-wide default. Returns undefined when neither is set;
 * callers report {@link MISSING_AUTHOR_MESSAGE} rather than inventing an
 * identity, since a wrong author on a shared note is worse than no note.
 */
export function resolveAuthor(config: ConfigLike = {}, env: NodeJS.ProcessEnv = process.env): string | undefined {
	const fromEnv = env[AUTHOR_ENV_VAR]?.trim()
	if (fromEnv) return fromEnv
	const fromConfig = config.username?.trim()
	if (fromConfig) return fromConfig
	return undefined
}
