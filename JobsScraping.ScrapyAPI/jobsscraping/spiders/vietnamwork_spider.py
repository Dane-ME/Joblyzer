import scrapy
from .base_spider import BaseJobSpider
from datetime import datetime
import json
import re
from w3lib.html import remove_tags

class VietnamWorkSpider(BaseJobSpider):
    name = 'vietnamwork'
    allowed_domains = ['vietnamworks.com', 'ms.vietnamworks.com']
    api_url = 'https://ms.vietnamworks.com/job-search/v1.0/search'
    
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 1,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'FEED_EXPORT_ENCODING': 'utf-8'
    }

    def start_requests(self):
        payload = {
            "userId": 7959290,
            "query": "",
            "filter": [
                {
                    "field": "jobFunction",
                    "value": "[{\"parentId\":5,\"childrenIds\":[-1]}]"
                }
            ],
            "ranges": [],
            "order": [{"field": "relevant", "value": "asc"}],
            "hitsPerPage": 50,
            "page": 1,  # page = 1 là trang thứ 2
            "retrieveFields": [
                "address","benefits","jobTitle","salaryMax","isSalaryVisible","jobLevelVI",
                "isShowLogo","salaryMin","companyLogo","userId","jobLevel","jobLevelId",
                "jobId","jobUrl","companyId","approvedOn","isAnonymous","alias","expiredOn",
                "industries","industriesV3","workingLocations","services","companyName",
                "salary","onlineOn","simpleServices","visibilityDisplay","isShowLogoInSearch",
                "priorityOrder","skills","profilePublishedSiteMask","jobDescription",
                "jobRequirement","prettySalary","requiredCoverLetter","languageSelectedVI",
                "languageSelected","languageSelectedId","typeWorkingId","createdOn",
                "isAdrLiteJob",
                "jobFunctionsV3"  # bổ sung để lấy trường yêu cầu
            ],
            "summaryVersion": ""
        }
        headers = {
            "Content-Type": "application/json",
            "Origin": "https://www.vietnamworks.com",
            "Referer": "https://www.vietnamworks.com/",
            "Accept": "application/json, text/plain, */*"
        }
        yield scrapy.Request(
            url=self.api_url,
            method="POST",
            body=json.dumps(payload),
            headers=headers,
            callback=self.parse_job_list,
            meta={'page': 1}
        )

    def parse_job_list(self, response):
        """Parse JSON từ API job search"""
        try:
            data = response.json()
        except Exception:
            self.logger.error("Không parse được JSON từ API.")
            return

        # Tùy cấu trúc API, cố gắng tìm mảng job
        jobs = None
        for key in ("data", "jobs", "hits", "results"):
            if isinstance(data.get(key), list):
                jobs = data.get(key)
                break
            if isinstance(data.get(key), dict) and isinstance(data[key].get("items"), list):
                jobs = data[key]["items"]
                break
        if jobs is None:
            # Một số API trả về trực tiếp list
            if isinstance(data, list):
                jobs = data
            else:
                # fallback tìm list lớn nhất
                jobs = next((v for v in data.values() if isinstance(v, list)), [])

        if not jobs:
            self.logger.info("Không có job nào trong response.")
            return

        for job in jobs:
            job_id = job.get("jobId")
            job_title = job.get("jobTitle")
            job_url = job.get("jobUrl")
            company_name = job.get("companyName")
            company_logo = job.get("companyLogo")
            working_locations = job.get("workingLocations") or []
            first_loc = working_locations[0] if working_locations else {}
            address = (first_loc or {}).get("address")
            city_vi = (first_loc or {}).get("cityNameVI")

            salary_min = job.get("salaryMin")
            salary_max = job.get("salaryMax")
            pretty_salary = job.get("prettySalary")

            skills = job.get("skills") or []
            skill_names = [s.get("skillName") for s in skills if isinstance(s, dict) and s.get("skillName")]

            job_level_vi = job.get("jobLevelVI")

            industries_v3 = job.get("industriesV3") or []
            industries_names_vi = [i.get("industryV3NameVI") for i in industries_v3 if isinstance(i, dict) and i.get("industryV3NameVI")]

            job_funcs_v3 = job.get("jobFunctionsV3") or []
            job_funcs_names_vi = [f.get("jobFunctionV3NameVI") for f in job_funcs_v3 if isinstance(f, dict) and f.get("jobFunctionV3NameVI")]

            created_on = job.get("createdOn")
            expired_on = job.get("expiredOn")

            base_data = {
                "jobId": job_id,
                "jobTitle": job_title,
                "jobUrl": job_url,
                "companyName": company_name,
                "companyLogo": company_logo,
                "workingLocations.address": address,
                "workingLocations.cityNameVI": city_vi,
                "salaryMin": salary_min,
                "salaryMax": salary_max,
                "prettySalary": pretty_salary,
                "skills.skillName": skill_names,
                "jobLevelVI": job_level_vi,
                "industriesV3.industryV3NameVI": industries_names_vi,
                "jobFunctionsV3.jobFunctionV3NameVI": job_funcs_names_vi,
                "createdOn": created_on,
                "expiredOn": expired_on,
                "source": "vietnamwork",
                "scraped_date": datetime.utcnow()
            }

            if job_url:
                # Theo yêu cầu: truy cập jobUrl với method POST để lấy JSON embed
                yield scrapy.Request(
                    url=job_url,
                    method="POST",
                    callback=self.parse_job_detail,
                    meta={"base_data": base_data, "jobId": job_id},
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                        "Origin": "https://www.vietnamworks.com",
                        "Referer": "https://www.vietnamworks.com/"
                    }
                )
            else:
                # Không có jobUrl thì yield dữ liệu cơ bản
                # TODO: Lưu base_data vào DB tại đây qua lớp CRUD/ORM của bạn.
                yield base_data

        # Có thể phân trang tiếp nếu cần: tăng page và gọi lại API
        # next_page = (response.meta.get('page') or 1) + 1
        # payload['page'] = next_page
        # yield scrapy.Request(...)

    def parse_job_detail(self, response):
        """Parse trang chi tiết: tìm JSON nhúng, lấy jobRequirement.jobLevel & yearsOfExperience, loại bỏ tag HTML."""
        base_data = response.meta.get("base_data") or {}
        text = response.text or ""

        # Thử nhiều pattern để lấy JSON embed:
        candidates = []

        # Pattern Next.js __NEXT_DATA__
        for m in re.finditer(r'<script[^>]*id="__NEXT_DATA__"[^>]*>\s*({.*?})\s*</script>', text, flags=re.DOTALL):
            candidates.append(m.group(1))

        # Pattern window.__NUXT__ =
        for m in re.finditer(r'window\.__NUXT__\s*=\s*({.*?});\s*</script>', text, flags=re.DOTALL):
            candidates.append(m.group(1))

        # Pattern application/json trong script
        for m in re.finditer(r'<script[^>]*type="application/json"[^>]*>\s*({.*?})\s*</script>', text, flags=re.DOTALL):
            candidates.append(m.group(1))

        # Fallback: JSON trong biến global nào đó
        for m in re.finditer(r'=\s*({\".*?\"})\s*[,;]</script>', text, flags=re.DOTALL):
            candidates.append(m.group(1))

        embed = None
        for raw in candidates:
            try:
                embed = json.loads(raw)
                break
            except Exception:
                continue

        job_level = None
        years_of_exp = None

        if embed:
            # Tìm đệ quy theo key trong embed JSON
            def walk_find(node, keys):
                found = []
                if isinstance(node, dict):
                    for k, v in node.items():
                        if k in keys:
                            found.append((k, v))
                        found.extend(walk_find(v, keys))
                elif isinstance(node, list):
                    for it in node:
                        found.extend(walk_find(it, keys))
                return found

            # Lấy jobRequirement trước
            job_req_nodes = [v for k, v in walk_find(embed, {"jobRequirement"})]
            # Nếu không có, cố gắng tìm trực tiếp keys cần
            if job_req_nodes:
                # Lấy node đầu tiên có dict
                jr = next((n for n in job_req_nodes if isinstance(n, (dict, str))), None)
                if isinstance(jr, dict):
                    job_level = jr.get("jobLevel")
                    years_of_exp = jr.get("yearsOfExperience")
                elif isinstance(jr, str):
                    # Nếu jobRequirement là HTML/string -> có thể chứa yearsOfExperience
                    # Giữ nguyên xử lý tiếp bên dưới
                    pass

            if job_level is None:
                jl_nodes = [v for k, v in walk_find(embed, {"jobLevel"})]
                job_level = jl_nodes[0] if jl_nodes else None

            if years_of_exp is None:
                y_nodes = [v for k, v in walk_find(embed, {"yearsOfExperience"})]
                years_of_exp = y_nodes[0] if y_nodes else None

        # Làm sạch nếu là string có tag HTML
        if isinstance(job_level, str):
            job_level = remove_tags(job_level).strip()
        if isinstance(years_of_exp, str):
            years_of_exp = remove_tags(years_of_exp).strip()

        job_data = dict(base_data)
        job_data.update({
            "jobRequirement.jobLevel": job_level,
            "jobRequirement.yearsOfExperience": years_of_exp
        })

        # TODO: Lưu job_data vào DB tại đây qua lớp CRUD/ORM của bạn (ví dụ: gọi hàm trong `database/crud.py`).
        yield job_data