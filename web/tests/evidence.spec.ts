import {test,expect} from "@playwright/test";

const routes=["","criteria","discovery","arms","cascade","safety","shadow","canary","handover","cost","try","data","report"];

test("all routes show the statement and work at phone width",async({page})=>{
 await page.setViewportSize({width:390,height:844});
 for(const route of routes){
  await page.goto("/cutover/"+(route?route+"/":""));
  await expect(page.locator("h1")).toBeVisible();
  await expect(page.locator("footer")).toContainText("It never closes a complaint");
  await expect(page.getByText("Loading evidence sheet.")).toHaveCount(0);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
 }
});

test("actual floor metrics match the committed evidence",async({page})=>{
 await page.goto("/cutover/arms/");
 const panel=page.getByRole("region",{name:"Actual baseline results"});
 await expect(panel).toContainText("103,889");
 await expect(panel).toContainText("78.45%");
 await expect(panel).toContainText("98.56%");
 await expect(panel).toContainText("73.42%");
 await expect(panel).toContainText("Load target missed");
 await page.getByRole("button",{name:"Switch to dark theme"}).click();
 await expect(page.locator("html")).toHaveAttribute("data-theme","dark");
 await page.reload();
 await expect(page.locator("html")).toHaveAttribute("data-theme","dark");
});

test("a first 503 wakes cleanly and persistent failure never claims a receipt",async({page})=>{
 let calls=0;
 let healthCalls=0;
 await page.route("**/health",route=>{
  if(route.request().method()==="HEAD")return route.fulfill({status:405});
  healthCalls++;
  return route.fulfill(healthCalls===1?{status:503,json:{detail:"synthetic_waking"}}:
   {status:200,json:{model_ready:false}});
 });
 await page.route("**/v1/triage",route=>{
  calls++;
  return route.fulfill({status:503,json:{detail:"synthetic_unavailable"}});
 });
 await page.goto("/cutover/try/");
 await page.getByRole("button",{name:/Request triage/}).click();
 await expect(page.locator(".try [role=alert]")).toContainText("No triage was confirmed");
 expect(calls).toBe(2);
 await expect(page.locator(".receipt")).toHaveCount(0);
 await page.unroute("**/v1/triage");
 calls=0;
 await page.route("**/v1/triage",route=>{
  calls++;
  return route.fulfill(calls===1?{status:503,json:{detail:"synthetic_waking"}}:{
   status:200,json:{receipt_id:"synthetic-not-a-database-receipt",release:"v1",mode:"synthetic_test",
   model_ready:false,decision:{action:"send_to_analyst",reason:"model_unavailable",queue:"OTHER",scores:{OTHER:1}}}
  });
 });
 await page.getByRole("button",{name:/Request triage/}).click();
 await expect(page.locator(".receipt")).toContainText("synthetic-not-a-database-receipt");
 expect(calls).toBe(2);
});

test("published API returns a durable receipt through the browser",async({page})=>{
 const health=await page.request.get("https://cutover-api.vercel.app/health");
 expect(health.status()).toBe(200);
 expect((await health.json()).model_ready).toBe(false);
 await page.goto("https://mekala27-45.github.io/cutover/try/");
 await page.getByLabel("Complaint narrative").fill("Authored browser verification: the dashboard clock loses its saved time.");
 const response=page.waitForResponse(r=>r.url().endsWith("/v1/triage")&&r.status()===200);
 await page.getByRole("button",{name:/Request triage/}).click();
 const receipt=await (await response).json();
 await expect(page.locator(".receipt")).toContainText(receipt.receipt_id);
 await expect(page.locator(".receipt")).toContainText("Send to an analyst");
 expect(receipt.mode).toBe("guard_only");
 console.log("CUTOVER_BROWSER_RECEIPT "+JSON.stringify(receipt));
});
