# Workbook inspection

- SHA-256: `1b7c0c937e5ea43e25c100d14670752736afc3a7ea6d191c1a303892396f620d`
- Inspected: 2026-11-08T13:54:39+00:00

| Sheet | Rows | Excel rows | Columns |
|---|---:|---|---:|
| `00_README` | 40 | 2–41 | 2 |
| `01_Excursion_Events` | 420 | 2–421 | 43 |
| `02_Product_Master` | 59 | 2–60 | 13 |
| `03_Facility_Registry` | 70 | 2–71 | 11 |
| `04_Carrier_Contracts` | 14 | 2–15 | 12 |
| `05_SOP_Index` | 203 | 2–204 | 12 |
| `06_Stability_Index` | 107 | 2–108 | 12 |
| `07_Alias_Observations` | 207 | 2–208 | 9 |
| `08_Reviewer_Queue_Log` | 200 | 2–201 | 14 |
| `09_Override_Reasons` | 24 | 2–25 | 5 |
| `10_Reviewer_Questions` | 12 | 2–13 | 5 |
| `11_Systems_Inventory` | 9 | 2–10 | 9 |
| `12_Tenant_Constraints` | 9 | 2–10 | 11 |
| `13_Volume_And_Cost` | 31 | 2–32 | 7 |
| `14_Incident_Log` | 6 | 2–7 | 6 |

## Findings

```json
{
  "event_tenants": {
    "REF-00002": 33,
    "REF-00010": 164,
    "REF-00025": 26,
    "REF-00062": 26,
    "REF-00101": 44,
    "REF-00109": 28,
    "REF-00152": 83,
    "REF-00186": 16
  },
  "event_tenants_without_constraint_row": [],
  "events_without_tenant": [],
  "product_identifiers_shared_across_tenants": {
    "internal_sku": [
      {
        "value": "ref-00028",
        "tenants": [
          "REF-00010",
          "REF-00025",
          "REF-00062",
          "REF-00109"
        ]
      },
      {
        "value": "ref-00056",
        "tenants": [
          "REF-00010",
          "REF-00025",
          "REF-00062",
          "REF-00109",
          "REF-00186"
        ]
      },
      {
        "value": "ref-00104",
        "tenants": [
          "REF-00010",
          "REF-00101",
          "REF-00109",
          "REF-00152"
        ]
      },
      {
        "value": "ref-00155",
        "tenants": [
          "REF-00109",
          "REF-00152"
        ]
      },
      {
        "value": "ref-00219",
        "tenants": [
          "REF-00101",
          "REF-00109",
          "REF-00152",
          "REF-00186"
        ]
      },
      {
        "value": "ref-00234",
        "tenants": [
          "REF-00002",
          "REF-00062",
          "REF-00101",
          "REF-00109",
          "REF-00186"
        ]
      },
      {
        "value": "ref-00246",
        "tenants": [
          "REF-00010",
          "REF-00062"
        ]
      },
      {
        "value": "ref-00280",
        "tenants": [
          "REF-00062",
          "REF-00152"
        ]
      },
      {
        "value": "ref-00387",
        "tenants": [
          "REF-00002",
          "REF-00010",
          "REF-00025",
          "REF-00186"
        ]
      },
      {
        "value": "ref-00428",
        "tenants": [
          "REF-00002",
          "REF-00010",
          "REF-00025",
          "REF-00062",
          "REF-00186"
        ]
      },
      {
        "value": "ref-00506",
        "tenants": [
          "REF-00010",
          "REF-00062"
        ]
      },
      {
        "value": "ref-00593",
        "tenants": [
          "REF-00002",
          "REF-00010",
          "REF-00025",
          "REF-00109"
        ]
      },
      {
        "value": "ref-01419",
        "tenants": [
          "REF-00002",
          "REF-00025",
          "REF-00109",
          "REF-00152"
        ]
      },
      {
        "value": "ref-01529",
        "tenants": [
          "REF-00002",
          "REF-00062",
          "REF-00186"
        ]
      }
    ],
    "gtin": [
      {
        "value": "ref-00036",
        "tenants": [
          "REF-00010",
          "REF-00025",
          "REF-00062"
        ]
      },
      {
        "value": "ref-00049",
        "tenants": [
          "REF-00010",
          "REF-00062",
          "REF-00186"
        ]
      },
      {
        "value": "ref-00077",
        "tenants": [
          "REF-00010",
          "REF-00062"
        ]
      },
      {
        "value": "ref-00097",
        "tenants": [
          "REF-00010",
          "REF-00101",
          "REF-00109",
          "REF-00152",
          "REF-00186"
        ]
      },
      {
        "value": "ref-00173",
        "tenants": [
          "REF-00002",
          "REF-00025",
          "REF-00109"
        ]
      },
      {
        "value": "ref-00347",
        "tenants": [
          "REF-00010",
          "REF-00025",
          "REF-00101",
          "REF-00109"
        ]
      },
      {
        "value": "ref-00483",
        "tenants": [
          "REF-00002",
          "REF-00062",
          "REF-00101",
          "REF-00109",
          "REF-00186"
        ]
      },
      {
        "value": "ref-00617",
        "tenants": [
          "REF-00101",
          "REF-00152"
        ]
      },
      {
        "value": "ref-00730",
        "tenants": [
          "REF-00002",
          "REF-00186"
        ]
      },
      {
        "value": "ref-01072",
        "tenants": [
          "REF-00109",
          "REF-00152"
        ]
      },
      {
        "value": "ref-01126",
        "tenants": [
          "REF-00010",
          "REF-00109"
        ]
      }
    ],
    "legacy_code": [],
    "brand_as_labelled": [
      {
        "value": "ref-00013",
        "tenants": [
          "REF-00002",
          "REF-00010",
          "REF-00025",
          "REF-00062",
          "REF-00101",
          "REF-00109",
          "REF-00186"
        ]
      },
      {
        "value": "ref-00134",
        "tenants": [
          "REF-00002",
          "REF-00010",
          "REF-00025",
          "REF-00101",
          "REF-00109"
        ]
      },
      {
        "value": "ref-00180",
        "tenants": [
          "REF-00002",
          "REF-00010",
          "REF-00025",
          "REF-00186"
        ]
      },
      {
        "value": "ref-00213",
        "tenants": [
          "REF-00025",
          "REF-00062",
          "REF-00152"
        ]
      },
      {
        "value": "ref-00225",
        "tenants": [
          "REF-00010",
          "REF-00101",
          "REF-00109",
          "REF-00152",
          "REF-00186"
        ]
      },
      {
        "value": "ref-00268",
        "tenants": [
          "REF-00002",
          "REF-00062",
          "REF-00101",
          "REF-00109",
          "REF-00186"
        ]
      },
      {
        "value": "ref-00284",
        "tenants": [
          "REF-00062",
          "REF-00101",
          "REF-00152"
        ]
      },
      {
        "value": "ref-00360",
        "tenants": [
          "REF-00010",
          "REF-00062",
          "REF-00109",
          "REF-00152"
        ]
      },
      {
        "value": "ref-00371",
        "tenants": [
          "REF-00002",
          "REF-00062",
          "REF-00186"
        ]
      },
      {
        "value": "ref-00408",
        "tenants": [
          "REF-00010",
          "REF-00062",
          "REF-00109",
          "REF-00186"
        ]
      },
      {
        "value": "ref-00461",
        "tenants": [
          "REF-00109",
          "REF-00152"
        ]
      },
      {
        "value": "ref-00546",
        "tenants": [
          "REF-00010",
          "REF-00062",
          "REF-00186"
        ]
      },
      {
        "value": "ref-00642",
        "tenants": [
          "REF-00010",
          "REF-00101",
          "REF-00109",
          "REF-00152"
        ]
      },
      {
        "value": "ref-01523",
        "tenants": [
          "REF-00002",
          "REF-00025",
          "REF-00109"
        ]
      }
    ]
  },
  "product_resolution_exact_tenant_scoped": {
    "missing_reference": 42,
    "resolved": 237,
    "unresolved": 141
  },
  "product_unresolved_examples": [
    "REF-00039",
    "REF-00061",
    "REF-00069",
    "REF-00088",
    "REF-00108",
    "REF-00119",
    "REF-00126",
    "REF-00138",
    "REF-00226",
    "REF-00237"
  ],
  "product_ambiguous_examples": [],
  "alias_observations": {
    "rows": 207,
    "status_column": null,
    "statuses": {}
  },
  "sop_overlaps": [
    {
      "tenant_code": "REF-00002",
      "doc_id": "ref-01728",
      "revisions": [
        "REDACTED - evaluation copy",
        "REDACTED - evaluation copy"
      ],
      "rows": [
        14,
        15
      ]
    },
    {
      "tenant_code": "REF-00002",
      "doc_id": "ref-01728",
      "revisions": [
        "REDACTED - evaluation copy",
        "REDACTED - evaluation copy"
      ],
      "rows": [
        15,
        16
      ]
    },
    {
      "tenant_code": "REF-00002",
      "doc_id": "ref-01728",
      "revisions": [
        "REDACTED - evaluation copy",
        "REDACTED - evaluation copy"
      ],
      "rows": [
        16,
        17
      ]
    },
    {
      "tenant_code": "REF-00010",
      "doc_id": "ref-01734",
      "revisions": [
        "REDACTED - evaluation copy",
        "REDACTED - evaluation copy"
      ],
      "rows": [
        35,
        36
      ]
    },
    {
      "tenant_code": "REF-00010",
      "doc_id": "ref-01734",
      "revisions": [
        "REDACTED - evaluation copy",
        "REDACTED - evaluation copy"
      ],
      "rows": [
        36,
        37
      ]
    },
    {
      "tenant_code": "REF-00010",
      "doc_id": "ref-01734",
      "revisions": [
        "REDACTED - evaluation copy",
        "REDACTED - evaluation copy"
      ],
      "rows": [
        37,
        38
      ]
    },
    {
      "tenant_code": "REF-00010",
      "doc_id": "ref-01734",
      "revisions": [
        "REDACTED - evaluation copy",
        "REDACTED - evaluation copy"
      ],
      "rows": [
        38,
        39
      ]
    },
    {
      "tenant_code": "REF-00025",
      "doc_id": "ref-01752",
      "revisions": [
        "REDACTED - evaluation copy",
        "REDACTED - evaluation copy"
      ],
      "rows": [
        92,
        93
      ]
    },
    {
      "tenant_code": "REF-00025",
      "doc_id": "ref-01754",
      "revisions": [
        "REDACTED - evaluation copy",
        "REDACTED - evaluation copy"
      ],
      "rows": [
        98,
        99
      ]
    },
    {
      "tenant_code": "REF-00186",
      "doc_id": "ref-01759",
      "revisions": [
        "REDACTED - evaluation copy",
        "REDACTED - evaluation copy"
      ],
      "rows": [
        112,
        113
      ]
    },
    {
      "tenant_code": "REF-00186",
      "doc_id": "ref-01759",
      "revisions": [
        "REDACTED - evaluation copy",
        "REDACTED - evaluation copy"
      ],
      "rows": [
        113,
        114
      ]
    },
    {
      "tenant_code": "REF-00186",
      "doc_id": "ref-01759",
      "revisions": [
        "REDACTED - evaluation copy",
        "REDACTED - evaluation copy"
      ],
      "rows": [
        114,
        115
      ]
    },
    {
      "tenant_code": "REF-00186",
      "doc_id": "ref-01759",
      "revisions": [
        "REDACTED - evaluation copy",
        "REDACTED - evaluation copy"
      ],
      "rows": [
        114,
        116
      ]
    },
    {
      "tenant_code": "REF-00186",
      "doc_id": "ref-01759",
      "revisions": [
        "REDACTED - evaluation copy",
        "REDACTED - evaluation copy"
      ],
      "rows": [
        115,
        116
      ]
    },
    {
      "tenant_code": "REF-00186",
      "doc_id": "ref-01760",
      "revisions": [
        "REDACTED - evaluation copy",
        "REDACTED - evaluation copy"
      ],
      "rows": [
        117,
        118
      ]
    },
    {
      "tenant_code": "REF-00186",
      "doc_id": "ref-01760",
      "revisions": [
        "REDACTED - evaluation copy",
        "REDACTED - evaluation copy"
      ],
      "rows": [
        118,
        119
      ]
    },
    {
      "tenant_code": "REF-00062",
      "doc_id": "ref-01774",
      "revisions": [
        "REDACTED - evaluation copy",
        "REDACTED - evaluation copy"
      ],
      "rows": [
        163,
        164
      ]
    },
    {
      "tenant_code": "REF-00062",
      "doc_id": "ref-01774",
      "revisions": [
        "REDACTED - evaluation copy",
        "REDACTED - evaluation copy"
      ],
      "rows": [
        164,
        165
      ]
    },
    {
      "tenant_code": "REF-00062",
      "doc_id": "ref-01774",
      "revisions": [
        "REDACTED - evaluation copy",
        "REDACTED - evaluation copy"
      ],
      "rows": [
        165,
        166
      ]
    },
    {
      "tenant_code": "REF-00101",
      "doc_id": "ref-01780",
      "revisions": [
        "REDACTED - evaluation copy",
        "REDACTED - evaluation copy"
      ],
      "rows": [
        183,
        184
      ]
    },
    {
      "tenant_code": "REF-00101",
      "doc_id": "ref-01780",
      "revisions": [
        "REDACTED - evaluation copy",
        "REDACTED - evaluation copy"
      ],
      "rows": [
        184,
        185
      ]
    },
    {
      "tenant_code": "REF-00101",
      "doc_id": "ref-01780",
      "revisions": [
        "REDACTED - evaluation copy",
        "REDACTED - evaluation copy"
      ],
      "rows": [
        185,
        186
      ]
    },
    {
      "tenant_code": "REF-00101",
      "doc_id": "ref-01784",
      "revisions": [
        "REDACTED - evaluation copy",
        "REDACTED - evaluation copy"
      ],
      "rows": [
        198,
        199
      ]
    },
    {
      "tenant_code": "REF-00101",
      "doc_id": "ref-01784",
      "revisions": [
        "REDACTED - evaluation copy",
        "REDACTED - evaluation copy"
      ],
      "rows": [
        199,
        200
      ]
    },
    {
      "tenant_code": "REF-00101",
      "doc_id": "ref-01784",
      "revisions": [
        "REDACTED - evaluation copy",
        "REDACTED - evaluation copy"
      ],
      "rows": [
        200,
        201
      ]
    },
    {
      "tenant_code": "REF-00101",
      "doc_id": "ref-01785",
      "revisions": [
        "REDACTED - evaluation copy",
        "REDACTED - evaluation copy"
      ],
      "rows": [
        202,
        203
      ]
    },
    {
      "tenant_code": "REF-00101",
      "doc_id": "ref-01785",
      "revisions": [
        "REDACTED - evaluation copy",
        "REDACTED - evaluation copy"
      ],
      "rows": [
        203,
        204
      ]
    }
  ],
  "sop_effective_from_date_only": 0,
  "sop_open_ended": 64,
  "sop_site_specific": 0,
  "product_to_stability_coverage": {
    "study_ref_found_same_tenant": 47,
    "study_ref_absent_from_index": 5,
    "product_without_study_ref": 7
  },
  "stability_path_does_not_mention_owner_tenant": {
    "column": "file_path_text",
    "count": 107,
    "examples": [
      {
        "study_ref": "REF-01786",
        "tenant_code": "REF-00002",
        "row": 2
      },
      {
        "study_ref": "REF-01522",
        "tenant_code": "REF-00002",
        "row": 3
      },
      {
        "study_ref": "REF-01524",
        "tenant_code": "REF-00002",
        "row": 4
      },
      {
        "study_ref": "REF-01789",
        "tenant_code": "REF-00002",
        "row": 5
      },
      {
        "study_ref": "REF-01791",
        "tenant_code": "REF-00002",
        "row": 6
      },
      {
        "study_ref": "REF-01792",
        "tenant_code": "REF-00002",
        "row": 7
      },
      {
        "study_ref": "REF-01528",
        "tenant_code": "REF-00002",
        "row": 8
      },
      {
        "study_ref": "REF-01530",
        "tenant_code": "REF-00002",
        "row": 9
      },
      {
        "study_ref": "REF-01795",
        "tenant_code": "REF-00002",
        "row": 10
      },
      {
        "study_ref": "REF-01532",
        "tenant_code": "REF-00002",
        "row": 11
      }
    ]
  },
  "stability_readability": {
    "REDACTED - evaluation copy": 107
  },
  "logger_firmware_builds": {
    "REDACTED - evaluation copy": 420
  },
  "events_gateway_gap_min": {
    "number_like": 420
  },
  "events_interpolated": {
    "text": 420
  },
  "events_readings_in_window": {
    "number_like": 420
  },
  "event_timestamps": {
    "alert_ts_utc": {
      "parsed": 420,
      "invalid": 0,
      "explicit_timezone_marker": 420
    },
    "excursion_start_utc": {
      "parsed": 420,
      "invalid": 0,
      "explicit_timezone_marker": 420
    },
    "excursion_end_utc": {
      "parsed": 420,
      "invalid": 0,
      "explicit_timezone_marker": 420
    }
  },
  "facility_timezones": {
    "UTC": 70
  },
  "carrier_rows": 0,
  "event_outcome_columns_excluded_from_assessment": [
    "triage_outcome",
    "rules_engine_recommendation",
    "final_disposition",
    "days_to_disposition",
    "hours_to_notification",
    "reopened_later"
  ]
}
```
