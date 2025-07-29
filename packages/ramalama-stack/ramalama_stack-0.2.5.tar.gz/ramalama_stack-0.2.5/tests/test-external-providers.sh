#!/bin/bash

main() {
  echo "===> starting 'test-external-providers'..."
  start_and_wait_for_ramalama_server
  test_ramalama_models
  test_ramalama_chat_completion
  start_and_wait_for_llama_stack_server
  test_llama_stack_models
  test_llama_stack_openai_models
  test_llama_stack_chat_completion
  test_llama_stack_openai_chat_completion
  echo "===> 'test-external-providers' completed successfully!"
}

TEST_UTILS=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
# shellcheck disable=SC2153,SC2034
INFERENCE_MODEL_NO_COLON=$(echo "$INFERENCE_MODEL" | tr ':' '_')
# shellcheck disable=SC1091
source "$TEST_UTILS/utils.sh"
main "$@"
exit 0
