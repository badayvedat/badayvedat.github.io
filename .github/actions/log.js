const core = require("@actions/core");
const github = require("@actions/github");
const fs = require("fs");

const GITHUB_COMMENT_BODY_LIMIT = 65536;

const createComment = async ({ commentBody, octokit }) => {
  const { context } = github;

  const response = await octokit.rest.issues
    .createComment({
      issueNumber: context.issue.number,
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

const updateComment = async ({ commentBody, commentId, octokit }) => {
  const { context } = github;
  console.log("start request: " + commentBody.length);
  const response = await octokit.rest.issues
    .updateComment({
      owner: context.repo.owner,
      repo: context.repo.repo,
      commentId: commentId,
      body: getMarkdownSummary(commentBody),
    })
    .catch((error) => {
      core.error(error);
      core.setFailed(error.message);
    });
  console.log("end request: " + response);

  return response.data.id;
};

const getMarkdownSummary = (body) => {
  const summaryBlock = "<summary>Show Output</summary>\n";
  const codeTicks = "\n```\n";
  const blockLength =
    `<details>${summaryBlock}${codeTicks}${codeTicks}</details>`.length;
  const output = `<details>${summaryBlock}${codeTicks}${body.slice(
    -(GITHUB_COMMENT_BODY_LIMIT - blockLength)
  )}${codeTicks}</details>`;
  return output;
};

const getLogFilePath = () => "output.log";
const getProcessSuccessFilePath = () => "SUCCESS";

const logOutputs = async ({ commentId, octokit }) => {
  const logPath = getLogFilePath();

  try {
    const data = fs.readFileSync(logPath, "utf8");
    console.log("start update: " + data.length);
    await updateComment({
      commentBody: data,
      commentId: commentId,
      octokit: octokit,
    });
    console.log("end update");
  } catch (error) {
    core.error(error);
    core.setFailed(error.message);
  }
};

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

const isProcessFinished = () => fs.existsSync(getProcessSuccessFilePath());

async function run() {
  try {
    const octokit = github.getOctokit(process.env.GITHUB_TOKEN);

    const commentId = await createComment({
      commentBody: getMarkdownSummary("Waiting for command logs.."),
      octokit: octokit,
    });

    const check_interval = 30 * 1000;
    setInterval(checkOutput, check_interval, {
      commentId: commentId,
      octokit: octokit,
    });
  } catch (error) {
    core.error(error);
    core.setFailed(error.message);
  }
}

run();
