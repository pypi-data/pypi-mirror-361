#! /usr/bin/env bash

function bluer_ugv_swallow_dataset_collect() {
    local options=$1
    local do_download=$(bluer_ai_option_int "$options" download 1)
    local do_upload=$(bluer_ai_option_int "$options" upload 0)
    local count=$(bluer_ai_option "$options" count -1)
    local update_metadata=$(bluer_ai_option_int "$options" update_metadata 0)

    if [[ "$do_download" == 1 ]]; then
        bluer_ugv_swallow_dataset_download
        [[ $? -ne 0 ]] && return 1
    fi

    local object_name=$(bluer_objects_metadata_get \
        key=dataset-object,object \
        $BLUER_UGV_SWALLOW_DATASET_LIST)
    object_name=$(bluer_ai_clarify_object $2 $object_name)
    bluer_ai_log "swallow dataset -> $object_name"

    bluer_ai_eval - \
        python3 -m bluer_ugv.swallow.dataset \
        collect \
        --count $count \
        --download $do_download \
        --object_name $object_name \
        --update_metadata $update_metadata \
        "${@:3}"
    [[ $? -ne 0 ]] && return 1

    if [[ "$do_upload" == 1 ]]; then
        bluer_ugv_swallow_dataset_upload
        bluer_objects_upload - $object_name
    fi
}
