#!/bin/bash
echo "--- dns ---"
getent hosts mrobo.uav.meituan.com || echo "DNS FAIL mrobo"
getent hosts egoops.meituan.com || echo "DNS FAIL egoops"
echo "--- https reachability ---"
curl -s -o /dev/null -w "mrobo: %{http_code} in %{time_total}s\n" --max-time 15 https://mrobo.uav.meituan.com/egoops/api/v1/users/me || echo "curl mrobo failed"
curl -s -o /dev/null -w "egoops: %{http_code} in %{time_total}s\n" --max-time 15 https://egoops.meituan.com/assignment || echo "curl egoops failed"
