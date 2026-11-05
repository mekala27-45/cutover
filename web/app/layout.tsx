import type { Metadata } from "next";
import "@fontsource/gabarito/600.css";
import "@fontsource/signika/400.css";
import "@fontsource/maple-mono/400.css";
import "./style.css";
export const metadata: Metadata = { title:"Cutover | Evidence before rollout", description:"Vehicle complaint triage, registered criteria and release evidence. Portfolio build in progress." };
export default function Layout({children}:{children:React.ReactNode}) {
 return <html lang="en"><body>{children}</body></html>;
}
