const core = require("@actions/core");
const github = require("@actions/github");
const fs = require("fs");

// Real limit is 65536. The remaining is left as an offset.
const GITHUB_COMMENT_BODY_LIMIT = 65000;

const getLogFilePath = () => "output.log";

const getProcessSuccessFilePath = () => "SUCCESS";

const createComment = async ({ commentBody, octokit }) => {
  const { context } = github;

  const response = await octokit.rest.issues
    .createComment({
      issue_number: context.issue.number,
      owner: context.repo.owner,
      repo: context.repo.repo,
      body: commentBody,
    })
    .catch((error) => {
      core.error(error);
      core.setFailed(error.message);
    });

  return response.data.id;
};

const updateComment = async ({ commentBody, commentID, octokit }) => {
  const { context } = github;
  console.log("commentBody length: " + commentBody.length);
  const response = await octokit.rest.issues
    .updateComment({
      owner: context.repo.owner,
      repo: context.repo.repo,
      commentId: commentID,
      body: getMarkdownSummary(commentBody),
    })
    .catch((error) => {
      console.log(error);
      core.error(error);
      core.setFailed(error.message);
    });
  console.log("response: " + response);
  return response.data.id;
};

const getMarkdownSummary = (body) => {
  const summaryBlock = "<summary>Show Output</summary>\n";
  const codeTicks = "\n```\n";
  const blockOffset = 100;
  const output = `<details>${summaryBlock}${codeTicks}${body.slice(
    -1000
  )}${codeTicks}</details>`;
  return output;
};

const logOutputs = async ({ commentId, octokit }) => {
  const logPath = getLogFilePath();

  try {
    const data = fs.readFileSync(logPath, "utf8");
    console.log("data length: ", + data.length);
    await updateComment({
      commentBody: data,
      commentId: commentId,
      octokit: octokit,
    });
  } catch (error) {
    core.error(error);
    core.setFailed(error.message);
  }
};

const isProcessFinished = () => fs.existsSync(getProcessSuccessFilePath());

const checkOutput = async ({ commentId, octokit }) => {
  await logOutputs({
    commentId: commentId,
    octokit: octokit,
  });

  if (isProcessFinished()) {
    await logOutputs({
      commentId: commentId,
      octokit: octokit,
    });

    process.exit(0);
  }
};

const run = async () => {
  try {
    const octokit = github.getOctokit(process.env.GITHUB_TOKEN);

    const commentId = await createComment({
      commentBody: getMarkdownSummary("Waiting for command logs.."),
      octokit: octokit,
    });

    const CHECK_INTERVAL = 30 * 1000;
    setInterval(checkOutput, CHECK_INTERVAL, {
      commentID: commentId,
      octokit: octokit,
    });
  } catch (error) {
    core.error(error);
    core.setFailed(error.message);
  }
};

run();
