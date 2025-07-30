from __future__ import annotations

from .common import (
    CerberusGorilleAnalysis,
    CerberusGorilleGcoreAnalysis,
)


class CerberusGorilleStatic(CerberusGorilleAnalysis):
    pass


class CerberusGorilleStaticGcore(CerberusGorilleGcoreAnalysis):
    pass

    def get_static_analysis_results(self):
        results = self.files[list(self.files)[0]].model_dump()
        if not results:
            return self.model_dump()

        status = results.get("status")
        site_info = results.get("site_info")
        matches = results.get("matches")

        if site_info:
            no_color_total = site_info.get("no_color_total")
            black_total = site_info.get("black_total")
            white_total = site_info.get("white_total")
            packer_total = site_info.get("packer_total")

            if "no_color_total" in site_info:
                site_info.pop("no_color_total")
            if "black_total" in site_info:
                site_info.pop("black_total")
            if "white_total" in site_info:
                site_info.pop("white_total")
            if "packer_total" in site_info:
                site_info.pop("packer_total")

            res = {
                "status": status,
                "no_color_total": no_color_total,
                "black_total": black_total,
                "white_total": white_total,
                "packer_total": packer_total,
                "site_info": site_info,
                "matches": matches
            }

        else:
            res = {
                "status": status
            }

        return res
