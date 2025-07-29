#! /usr/bin/env bash

function test_bluer_algo_image_classifier_dataset_review() {
    local options=$1

    bluer_ai_eval ,$options \
        bluer_algo_image_classifier_dataset_review \
        ,$options \
        $BLUER_ALGO_FRUITS_360_TEST_DATASET
}
