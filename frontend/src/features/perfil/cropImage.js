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

  // Define o tamanho do canvas para o tamanho do recorte final
  canvas.width = pixelCrop.width;
  canvas.height = pixelCrop.height;

  // Desenha a imagem recortada
  ctx.drawImage(
    image,
    pixelCrop.x,
    pixelCrop.y,
    pixelCrop.width,
    pixelCrop.height,
    0,
    0,
    pixelCrop.width,
    pixelCrop.height
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
