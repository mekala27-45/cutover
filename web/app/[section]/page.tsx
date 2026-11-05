import Sheet from "../sheet";
const sections=["criteria","discovery","arms","cascade","safety","shadow","canary","handover","cost","try","data","report"];
export function generateStaticParams(){return sections.map(section=>({section}));}
export default async function Page({params}:{params:Promise<{section:string}>}){
 const {section}=await params;
 return <Sheet section={section}/>;
}
