import { validateManifest, verifySignature } from "./plugin-security";
import { localPlugin } from "./local-plugin";

const LOCAL_PLUGIN_ID = "local";

export function loadPlugin(id: string, manifest: unknown, signature: string) {
  if (id !== LOCAL_PLUGIN_ID) throw new Error("Unknown plugin");
  const validated = validateManifest(manifest);
  if (!verifySignature(validated, signature)) throw new Error("Invalid signature");
  return localPlugin;
}
