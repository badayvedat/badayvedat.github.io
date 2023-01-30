const core = require("@actions/core");
const github = require("@actions/github");
const fs = require("fs");

const GITHUB_COMMENT_BODY_LIMIT = 65536;

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
      console.error(error);
    });

  return response.data.id;
};

const updateComment = async ({ commentBody, commentID, octokit }) => {
  const { context } = github;
  console.log(commentBody.length);
  const response = await octokit.rest.issues
    .updateComment({
      owner: context.repo.owner,
      repo: context.repo.repo,
      comment_id: commentID,
      body: getMarkdownSummary(commentBody),
    })
    .catch((error) => {
      console.error(error);
    });
  console.log(response);
  return response.data.id;
};

const getMarkdownSummary = (body) => {
  const summaryBlock = "<summary>Show Output</summary>\n";
  const codeTicks = "\n```\n";
  const output = `<details>${summaryBlock}${codeTicks}${body.slice(
    -(GITHUB_COMMENT_BODY_LIMIT - blockLength)
  )}${codeTicks}</details>`;
  return output;
};

const logOutputs = async ({ commentId, octokit }) => {
  const logPath = getLogFilePath();

  try {
    const data = fs.readFileSync(logPath, "utf8");
    await updateComment({
      commentBody: data,
      commentId: commentId,
      octokit: octokit,
    });
  } catch (error) {
    console.error(error);
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
