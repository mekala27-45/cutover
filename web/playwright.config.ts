import {defineConfig} from "@playwright/test";
export default defineConfig({
 testDir:"./tests",workers:1,retries:0,timeout:60000,globalTimeout:300000,
 reporter:[["list"],["json",{outputFile:"test-results/summary.json"}]],
 use:{baseURL:"http://127.0.0.1:4173",browserName:"chromium",trace:"off",screenshot:"only-on-failure"},
 webServer:{command:"python -m http.server 4173 --directory .preview",url:"http://127.0.0.1:4173/cutover/",reuseExistingServer:false}
});
