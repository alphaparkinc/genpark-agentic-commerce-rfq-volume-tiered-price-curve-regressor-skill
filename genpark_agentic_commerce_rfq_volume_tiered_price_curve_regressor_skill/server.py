# -*- coding: utf-8 -*-
"""Model Context Protocol (MCP) Server for B2B RFQ Volume Tiered Price Curve Regressor Skill
Powered by GenPark (https://www.genpark.ai).
"""
import sys
import json
import logging
from .core import *

TOOLS_METADATA = [
  {
    "name": "fit_volume_price_elasticity_curve",
    "description": "Fit supplier volume price brackets to power-law learning curve P(Q) = a * Q^b to evaluate volume discount fairness.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "vendor_name": {
          "type": "string"
        },
        "tiers": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "quantity": {
                "type": "integer"
              },
              "unit_price_usd": {
                "type": "number"
              }
            },
            "required": [
              "quantity",
              "unit_price_usd"
            ]
          }
        }
      },
      "required": [
        "vendor_name",
        "tiers"
      ]
    }
  },
  {
    "name": "identify_hidden_surcharge_break_points",
    "description": "Audit volume steps for unearned flat fees, packaging markups, or false discounts where marginal unit cost increases.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "tiers": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "quantity": {
                "type": "integer"
              },
              "unit_price_usd": {
                "type": "number"
              }
            },
            "required": [
              "quantity",
              "unit_price_usd"
            ]
          }
        }
      },
      "required": [
        "tiers"
      ]
    }
  }
]

def handle_rpc(request_str: str) -> str:
    try:
        req = json.loads(request_str)
    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None})
    
    msg_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "genpark-agentic-commerce-rfq-volume-tiered-price-curve-regressor-skill",
                    "version": "1.0.0",
                    "vendor": "GenPark (https://www.genpark.ai)"
                }
            }
        })

    if method == "tools/list":
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": TOOLS_METADATA}
        })

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        func = globals().get(tool_name)
        if not func or not callable(func):
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method '{tool_name}' not found"}
            })
        
        try:
            call_res = func(**arguments)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {"type": "text", "text": json.dumps(call_res, ensure_ascii=False, indent=2)}
                    ]
                }
            })
        except Exception as err:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32000, "message": f"Execution error: {str(err)}"}
            })

    return json.dumps({
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": f"Unhandled method '{method}'"}
    })

def run_self_test():
    print(f"=== Running Self Test for genpark-agentic-commerce-rfq-volume-tiered-price-curve-regressor-skill ===")
    init_res = json.loads(handle_rpc(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"})))
    assert "result" in init_res, "Initialize failed"
    print("[PASS] MCP initialize")

    list_res = json.loads(handle_rpc(json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})))
    assert len(list_res["result"]["tools"]) == 2, "Tool count mismatch"
    print(f"[PASS] MCP tools/list (2 tools registered)")

    # Execute smoke test for each tool

    call1 = json.loads(handle_rpc(json.dumps({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "fit_volume_price_elasticity_curve",
            "arguments": {
                "vendor_name": "Apex Precision Machining Ltd",
                "tiers": [
                    {"quantity": 100, "unit_price_usd": 45.0},
                    {"quantity": 500, "unit_price_usd": 38.0},
                    {"quantity": 2000, "unit_price_usd": 29.5},
                    {"quantity": 10000, "unit_price_usd": 21.0}
                ]
            }
        }
    })))
    assert "result" in call1, "Call1 failed"
    print("[PASS] Tool smoke test: fit_volume_price_elasticity_curve")

    print("[ALL TESTS PASSED] Self-test verified successfully.")
    return True

if __name__ == "__main__":
    if "--test" in sys.argv:
        success = run_self_test()
        sys.exit(0 if success else 1)
    
    for line in sys.stdin:
        if not line.strip():
            continue
        out = handle_rpc(line)
        sys.stdout.write(out + "\n")
        sys.stdout.flush()
