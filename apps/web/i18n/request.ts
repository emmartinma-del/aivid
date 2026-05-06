import { getRequestConfig } from "next-intl/server";
import { cookies } from "next/headers";

export default getRequestConfig(async () => {
  const cookieStore = cookies();
  const locale = cookieStore.get("locale")?.value ?? "de";
  const supported = ["de", "en"];
  const resolvedLocale = supported.includes(locale) ? locale : "de";

  return {
    locale: resolvedLocale,
    messages: (await import(`../messages/${resolvedLocale}.json`)).default,
  };
});
