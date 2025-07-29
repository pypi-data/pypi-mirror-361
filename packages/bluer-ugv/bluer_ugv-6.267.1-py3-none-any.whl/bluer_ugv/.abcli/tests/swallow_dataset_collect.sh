#! /usr/bin/env bash

function test_bluer_ugv_swallow_collect() {
    local options=$1

    local object_name=test_bluer_ugv_swallow_collect-$(bluer_ai_string_timestamp_short)

    bluer_ugv_swallow_dataset_collect \
        $options,count=2 \
        $object_name
}
