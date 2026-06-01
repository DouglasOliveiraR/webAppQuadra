/**
 * Cria um objeto HTMLImageElement a partir de uma URL de imagem.
 * @param {string} url - URL ou base64 da imagem.
 * @returns {Promise<HTMLImageElement>}
 */
export const createImage = (url) =>
  new Promise((resolve, reject) => {
    const image = new Image();
    image.addEventListener('load', () => resolve(image));
    image.addEventListener('error', (error) => reject(error));
    image.setAttribute('crossOrigin', 'anonymous'); // Evita problemas de CORS no Canvas
    image.src = url;
  });

/**
 * Recorta a imagem original utilizando as coordenadas fornecidas e retorna um Blob.
 * @param {string} imageSrc - URL ou base64 da imagem original.
 * @param {Object} pixelCrop - Coordenadas e dimensões de recorte { x, y, width, height }.
 * @returns {Promise<Blob>}
 */
export async function getCroppedImg(imageSrc, pixelCrop) {
  const image = await createImage(imageSrc);
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');

  if (!ctx) {
    return null;
  }

  // Forçar o tamanho máximo de 500x500 para evitar erro de memória no Canvas do iPhone (iOS Safari)
  const MAX_SIZE = 500;
  canvas.width = MAX_SIZE;
  canvas.height = MAX_SIZE;

  // Desenha a imagem recortada e redimensionada
  ctx.drawImage(
    image,
    pixelCrop.x,
    pixelCrop.y,
    pixelCrop.width,
    pixelCrop.height,
    0,
    0,
    MAX_SIZE,
    MAX_SIZE
  );

  // Retorna como Promise com o Blob final da imagem
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) {
        resolve(blob);
      } else {
        reject(new Error('Canvas is empty'));
      }
    }, 'image/jpeg', 0.8);
  });
}
